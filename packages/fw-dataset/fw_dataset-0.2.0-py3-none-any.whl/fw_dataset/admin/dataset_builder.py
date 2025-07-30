"""Module to build a dataset from a Flywheel project."""

import json
import logging
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Dict

import orjson
import pandas as pd
from flywheel import Client as SDKClient
from flywheel import Project
from fsspec import AbstractFileSystem
from fw_client import FWClient as APIClient

from ..filesystem import (
    _get_storage_credentials,
    decompress_stream,
    get_fs_type,
)
from ..fw_dataset import Dataset
from .admin_helpers import (
    drop_schema_properties,
    enforce_field_types,
    save_custom_info_table,
    save_pyarrow_table,
    save_schema,
    validate_retained_columns,
)
from .constants import (
    INFO_SCHEMA,
    POPULATE_CUSTOM_INFO,
    POPULATE_TABULAR_DATA,
    SNAPSHOT_MAPPINGS,
    SNAPSHOT_TIMEOUT,
    TABLES,
    DataModel,
)
from .custom_info_table_builder import CustomInfoTableBuilder
from .exceptions import SnapshotCreationError
from .tabular_file_table_builder import TabularFileTableBuilder

log = logging.getLogger(__name__)


class DatasetBuilder:
    """Class to build a dataset from a Flywheel project."""

    # TODO: This class is doing too much. It should be broken up into smaller classes
    #       that handle the different parts of the dataset building process.
    #      - Primary ETL
    #      - Secondary ETL
    #      - Custom ETL
    #      - Snapshot Management

    # TODO: create a "hide_tables" function that will hide tables from the UI and API
    #       - put in {schema_path}/hidden/{table_name}.schema.json
    # TODO: "list_hidden_tables" function that will list the hidden tables
    # TODO: "unhide_table" function that will unhide a table

    def __init__(
        self,
        api_key: str = None,
        project_id: str = None,
        project_path: str = None,
        storage_id: str = None,
        storage_label: str = None,
        credentials: dict = None,
        root_path: str | Path = None,
        control_columns: dict = None,
    ) -> None:
        """Initialize the dataset builder object with essential parameters.

        Set up the dataset builder object to render a Flywheel project into a dataset.

        The following combinations of parameters are required to set up the dataset:
        - api_key
        - project_id or project_path
        - storage_id or storage_label or credentials
            - credentials must be a dictionary with the following format:
                {
                    "url": "{fs_type}://{bucket}?{credentials}",
                }
                see get_storage_filesystem for more information.

        `control_columns` is a dictionary that contains the control columns for the tables.
        - it has the following format:
            {
                "<container_name>": [<list of columns>],
                ...
            }

        Args:
            api_key (str, optional): Valid Flywheel API-KEY. Defaults to None.
            project_id (str, optional): Valid Flywheel Project ID. Defaults to None.
            project_path (str, optional): Path to Flywheel Project. Defaults to None.
            storage_id (str, optional): Valid Flywheel Storage ID. Defaults to None.
            storage_label (str, optional): Label to Valid Flywheel Storage. Defaults to None.
            credentials (dict, optional): Dictionary of Valid Cloud Credentials. Defaults to {}.
            control_columns (dict, optional): Control columns for the tables. Defaults to {}.
            root_path (str, optional): Path to Local Filesystem. Defaults to None.

        Raises:
            ValueError: You must provide an API key for the Flywheel instance.
            ValueError: Dataset not found: {project_id}
            ValueError: Dataset not found: {project_path}
            ValueError: You must provide either a project_id or a path to a project
            ValueError: Storage not found: {storage_id}
            ValueError: Storage not found: {storage_label}
            ValueError: Invalid Credentials
            ValueError: You must provide a storage_id, storage_label, valid credentials,
            a root_path to a local filesystem, or existing directives must exist in the
            project.

        # TODO: I want the options to search for the project by path.
           - Set the dataset.info to the project information instantiate the dataset
             object from the project information.
           - Check to see if the project/group/site has permissions to access the
             storage
             - Error? Maybe... discuss. Doesn't see to be a problem.
        """
        self.version_label = None
        self.partition_size = 10_000  # TODO: Make this a parameter in constants.py

        # TODO: Change this to be consistent with the "dataset" object
        self.tables = {}

        if (
            api_key is None
            and os.environ.get("FW_HOSTNAME")
            and os.environ.get("FW_WS_API_KEY")
        ):
            api_key = (
                f"{os.environ.get('FW_HOSTNAME')}:{os.environ.get('FW_WS_API_KEY')}"
            )
        elif api_key is None:
            raise ValueError("You must provide an API key for the Flywheel instance.")

        self.api_key = api_key

        # TODO: Check if the API key is valid, if not raise an error
        self.sdk_client = SDKClient(self.api_key)
        self.api_client = APIClient(api_key=self.api_key)

        # This will be used in the default dataset path
        # {root}/datasets/{instance_address}/{group}/{project_id}
        self.instance_address = self.api_client.config.baseurl.split("/")[-1]

        # TODO: Check the project for an existing dataset.info record. This will contain
        # the storage_id... if it is there...but then...we don't know if the storage
        # object has been deleted??? that is why we try to get it....
        # If a project ID or a Project path have been provided.
        if project_id or project_path:
            self.set_project(project_id=project_id, project_path=project_path)
        else:
            raise ValueError(
                "You must provide either a project_id or a path to a project"
            )

        # If a Storage ID or a Storage Label have been provided.
        if (
            storage_id
            or storage_label
            or credentials
            or root_path
            or self.dataset.dataset_info.get("storage_id")
        ):
            self.set_storage(
                storage_id=storage_id,
                storage_label=storage_label,
                credentials=credentials,
                root_path=root_path,
            )
        else:
            raise ValueError(
                "You must provide a storage_id, storage_label, valid credentials, "
                "a root_path to a local filesystem, or "
                "existing directives must exist in the project."
            )

        # TODO: Use jsonschema.validate to validate the control_columns
        self.control_columns = control_columns if control_columns else {}

    def set_project(
        self, project_id: str = None, project_path: str = None, project: Project = None
    ):
        """Set the project object from the project_id or project_path.

        Args:
            project_id (str, optional): The project ID. Defaults to None.
            project_path (str, optional): The FW Path to the project. Defaults to None.
            project (Project, optional): A Project object. Defaults to None.

        Raises:
            ValueError: Dataset not found: {project_id}
            ValueError: Dataset not found: {project_path}
            ValueError: You must provide either a dataset_id or a path to a dataset
        """
        if project_id and not project:
            try:
                project = self.sdk_client.get(project_id)
            except Exception as e:
                raise ValueError(f"Dataset not found: {project_id}") from e
        elif project_path and not project:
            if project_path.startswith("fw://"):
                stripped_path = project_path.replace("fw://", "")
            else:
                stripped_path = project_path
            try:
                project = self.sdk_client.lookup(stripped_path)
            except Exception as e:
                raise ValueError(f"Dataset not found: {stripped_path}") from e
        elif not project:
            raise ValueError(
                "You must provide either a dataset_id or a path to a dataset"
            )
        self.project = project

        self.dataset = self.set_dataset(project=project)

    def set_dataset(
        self,
        project: Project = None,
        dataset_id: str = None,
        name: str = None,
        description: str = None,
    ) -> Dataset:
        """Set the dataset object from the project.

        Args:
            project (Project, optional): The Flywheel Project. Defaults to None.
            dataset_id (str, optional): The id of the dataset. Defaults to None.
            name (str, optional): Name of the dataset. Defaults to None.
            description (str, optional): Description of the dataset. Defaults to None.

        Raises:
            ValueError: You must provide a project or a dataset_id and name.

        Returns:
            Dataset: An instance of the Dataset object.
        """
        if project:
            dataset_id = project.id
            name = project.label
            description = project.description
            dataset_info = project.info.get("dataset", {})
            return Dataset(
                id=dataset_id,
                name=name,
                description=description,
                dataset_info=dataset_info,
            )
        elif dataset_id and name:
            return Dataset(id=dataset_id, name=name, description=description)
        else:
            raise ValueError("You must provide a project or a dataset_id and name.")

    def set_storage_prefix(self, prefix: str = None):
        """Set the storage prefix for the dataset.

        This function prevents collisions between datasets by appending the default
        prefix to the provided prefix in a determined fashion.

        Args:
            prefix (str, optional): The existing prefix for the storage. Defaults to None.
        """
        # The default prefix should be the instance address, group, and project id
        default_prefix = (
            f"datasets/{self.instance_address}/{self.project.group}/{self.project.id}"
        )
        # if the prefix is empty
        if prefix == default_prefix:
            pass
        elif not prefix:
            prefix = default_prefix
        # else if the prefix ends in "dataset" or "datasets"
        elif prefix.split("/")[-1] in ("dataset", "datasets"):
            prefix += f"/{default_prefix[9:]}"
        # else, append the default prefix to the provided prefix to prevent collisions
        else:
            prefix += f"/{default_prefix}"
            log.warning(
                "The existing prefix is neither blank or in the expected format. "
                "Appending the default prefix to the provided external storage prefix."
            )
        return prefix

    def set_storage(
        self,
        storage_id: str = None,
        storage_label: str = None,
        credentials: dict = None,
        root_path: str | Path = None,
    ):
        """Set the storage for the dataset.

        If the project.info["dataset"] has a storage_id, use that to get the storage
        Else one of the following must be provided:
        - storage_id
        - storage_label
        - credentials
            - See get_storage_filesystem for the format
        - root_path

        TODO: Tidy up this function. It is a bit of a mess.

        Args:
            storage_id (str, optional): ID of the Flywheel Storage. Defaults to None.
            storage_label (str, optional): Label of the Flywheel Storage. Defaults to None.
            credentials (dict, optional): Credentials of Cloud Storage. Defaults to {}.
            root_path (str|Path, optional): Path to local filesystem. Defaults to None.

        Raises:
            ValueError: You must set a project before setting the storage.
            ValueError: Storage not found: {storage_id}
            ValueError: Storage not found: {storage_label}
            ValueError: Invalid Credentials
            ValueError: You must provide a storage_id, storage_label, valid credentials, a root_path to a local filesystem, or existing directives must exist in the project.
        """
        if credentials is None:
            credentials = {}

        if not (self.project or self.dataset):
            raise ValueError(
                "You must have the project set before setting the storage."
            )
        # Check if the project has a dataset.info record and an existing prefix
        existing_valid_prefix = False
        # Prioritize existing dataset info on project
        if self.dataset.dataset_info.get("storage_id"):
            log.info("Storage ID found in dataset info.")
            dataset_info = self.dataset.dataset_info
            storage_id = dataset_info.get("storage_id")
            fs_type = dataset_info.get("type")
            storage_json = {
                "_id": storage_id,
                "config": {
                    "type": dataset_info.get("type"),
                    "bucket": dataset_info.get("bucket"),
                    "prefix": dataset_info.get("prefix"),
                },
                "label": dataset_info.get("label"),
            }
            credentials = _get_storage_credentials(self.api_client, fs_type, storage_id)
            existing_valid_prefix = True
        # The fs_type can be s3, gs, az, fs, or local.
        elif storage_id:
            try:
                storage_json = self.api_client.get(f"/xfer/storages/{storage_id}")
                fs_type = storage_json.get("config", {}).get("type")
                credentials = _get_storage_credentials(
                    self.api_client, fs_type, storage_id
                )
            except Exception as e:
                raise ValueError(f"Storage not found: {storage_id}") from e
        elif storage_label:
            storages = self.api_client.get("/xfer/storages")["results"]
            storage = [stor for stor in storages if stor["label"] == storage_label]
            if storage:
                storage_json = storage[0]
                storage_id = storage_json["_id"]
                fs_type = storage_json.get("config", {}).get("type")
                credentials = _get_storage_credentials(
                    self.api_client, fs_type, storage_id
                )
            else:
                raise ValueError(f"Storage not found: {storage_label}")
        elif credentials:
            try:
                fs_type = credentials.get("url").split(":")[0]
                storage_json = {"config": {"type": fs_type}}
            except Exception as e:
                raise ValueError("Invalid Credentials") from e
        elif root_path:
            fs_type = "fs"
            credentials = {"root_path": str(root_path)}
            prefix = (
                f"datasets/{self.instance_address}/"
                f"{self.project.group}/{self.project.id}"
            )
            storage_json = {
                "label": self.project.label,
                "config": {"type": fs_type, "bucket": str(root_path), "prefix": prefix},
            }

        else:
            raise ValueError(
                "You must provide a storage_id, storage_label, valid credentials, "
                "a root_path to a local filesystem, or "
                "existing directives must exist in the project."
            )

        # TODO: Check if I really need to carry this around
        self.storage_json = storage_json

        # If the prefix is not set, set it
        if not existing_valid_prefix:
            storage_json["config"]["prefix"] = self.set_storage_prefix(
                storage_json["config"]["prefix"]
            )
        log.info("Prefix set to: %s", storage_json["config"]["prefix"])
        self.dataset.dataset_info.update(
            {
                "storage_id": storage_id,
                "type": fs_type,
                "bucket": storage_json.get("config", {}).get("bucket"),
                "prefix": storage_json.get("config", {}).get("prefix"),
                "label": storage_json.get("label"),
            }
        )

        self.dataset.set_filesystem(get_fs_type(fs_type), credentials)
        self.dataset.setup_paths()

    def save_dataset_info(self):
        """Save the dataset info to the project."""
        self.project.update_info(dataset=self.dataset.dataset_info)
        self.dataset.save()

    def check_storage_permissions(self):
        """Check if the project has permissions to access the storage."""
        if self.storage_json and self.project:
            refs = self.storage_json.get("refs")
            if not ((proj_id := refs.get("project")) and (proj_id == self.project.id)):
                log.warning(f"Project {self.project.label} does not have permissions.")
            elif not ((group := refs.get("group")) and (group == self.project.group)):
                log.warning(f"Group {group} does not have permission")
        else:
            log.error(
                "You need to have the project and the storage set before checking permissions."
            )

    @classmethod
    def is_populated(
        cls, filesystem: AbstractFileSystem, expected_dataset_path: str | Path
    ) -> bool:
        """Check if the dataset is populated with the expected artifacts

        See the get_storage_filesystem function to initialize a filesystem object with
        the correct credentials.

        The expected_dataset_path is typically the path from the root to the dataset
        e.g. {bucket}/datasets/{instance_address}/{group}/{project_id}

        Or, more simply, {bucket}/{prefix} from the project.info.dataset record.

        TODO: Convert expected_path using a CloudPath class that encapsulates
        the path and filesystem.

        TODO: Consider putting this function in the fw_dataset class

        Args:
            filesystem (AbstractFileSystem): The filesystem object to use.
            expected_dataset_path (str): The bucket or root_path of the dataset

        Returns:
            bool: Whether the dataset is populated or not.
        """
        expected_dataset_path_latest = Path(expected_dataset_path) / "latest"
        for table in TABLES:
            # Check for the existence of the schema
            # NOTE: We may want to hide tables such that they are not accessible from
            #       the API or the UI. Proposed is ./hidden/{table_name}.schema.json
            # if not (dataset_path / f"schemas/{table['id']}.json").exists():
            #     return False
            # Check for the existence of the table
            table_path = expected_dataset_path_latest / f"tables/{table['id']}/"
            # TODO: I want `table_path.exists()` to work with its own filesystem object
            if not filesystem.exists(str(table_path)):
                return False
            # Check for the existence of the parquet files for the table
            # TODO: ensure the hive configuration is detected
            parquet_files = list(filesystem.glob(str(table_path / "*.parquet")))
            if not parquet_files:
                return False

        # Check for the existence of the project record
        if not (
            filesystem.exists(
                str(expected_dataset_path_latest / "provenance" / "project.json")
            )
        ):
            return False

        return True

    def create_snapshot(self) -> Dict:
        """Create a snapshot of the dataset and wait for it to complete.

        Snapshots have the following statuses:
        - "pending"
        - "in_progress"
        - "complete"
        - "failed"

        TODO: Make this asynchronous and use a callback to notify the user when it is
        complete.

        Returns:
            Dict: The snapshot of the dataset.
        """
        start_creation = time.time()
        snapshot = self.api_client.post(
            f"/snapshot/projects/{self.dataset.id}/snapshots"
        )
        log.info("Creating snapshot...")
        while snapshot and snapshot["status"] != "complete":
            time.sleep(10)
            response = self.api_client.get(
                f"/snapshot/projects/{self.dataset.id}/snapshots"
            )
            if not response:
                raise SnapshotCreationError("Snapshot creation failed.")

            snapshot = response[-1]
            creation_time = time.time() - start_creation
            if creation_time > SNAPSHOT_TIMEOUT or snapshot["status"] == "failed":
                raise SnapshotCreationError("Snapshot creation timed out or failed.")
        return snapshot

    def create_or_get_latest_snapshot(self, force_new: bool = False) -> None:
        """Create or get the latest snapshot of the dataset.

        Args:
            force_new (bool, optional): Force the creation of a new snapshot. Defaults
            to False.

        Returns:
            None
        """

        # Check if a snapshot exists, if not create one
        snapshots = self.api_client.get(
            f"/snapshot/projects/{self.project.id}/snapshots"
        )
        # TODO: The Snapshot_id is the version of the dataset
        # TODO: Save the snapshot record to the dataset directory
        if not snapshots or force_new:
            self.snapshot = self.create_snapshot()
        else:
            self.snapshot = snapshots[-1]

        self.dataset.version = self.snapshot["_id"]
        if self.version_label is None:
            self.version_label = self.snapshot["_id"]
        self.dataset.version_label = self.version_label
        self.dataset.created = self.snapshot["created"]
        # Create the dataset directories for the snapshot version
        self.dataset.setup_paths(version=self.dataset.version)

    def decompress_snapshot(self) -> Path:
        """Decompress the snapshot of the dataset."""
        snapshot_id = self.snapshot["_id"]

        # Write the snapshot record to a file
        with self.dataset._fs.open(
            self.dataset.paths.provenance_path / "snapshot_info.json",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(json.dumps(self.snapshot, default=str, indent=4))

        # TODO: Is there a way to stream the download directly to the decompression
        # step? Or directly to a file? This would save RAM.
        log.info("Downloading snapshot...")
        resp = self.api_client.get(
            f"/snapshot/projects/{self.dataset.id}/snapshots/{snapshot_id}", stream=True
        )
        # TODO: Check the date of the snapshot and only download if it is newer
        snapshot_file_path = self.dataset.paths.provenance_path / "snapshot.db.gz"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            decompressed_path = temp_file.name

        with self.dataset._fs.open(snapshot_file_path, "wb") as fp:
            fp.write(resp.content)

        # Decompress the downloaded file and write it a local temp file
        log.info("Decompressing snapshot...")
        with self.dataset._fs.open(snapshot_file_path, "rb") as f_in:
            with open(decompressed_path, "wb") as f_out:
                for chunk in decompress_stream(f_in):
                    f_out.write(chunk)

        return decompressed_path

    def extract_custom_info_from_container_records(
        self, container_records: list, container_type: str
    ) -> pd.DataFrame:
        """Extract custom information from container records.

        Args:
            container_records (list): List of container records as dictionaries.
            container_type (str): The type of container.

        Returns:
            pd.DataFrame: A DataFrame containing the custom information.
        """
        # Initializing the custom_info_df to the INFO_SCHEMA properties
        columns_list = list(INFO_SCHEMA.properties.keys())
        empty_custom_info_df = pd.DataFrame(columns=columns_list)
        custom_info_file_list = []
        for row in container_records:
            if custom_info := row.get("info"):
                if container_type == "file":
                    container_id = row["_id"].get("file_id")
                else:
                    container_id = row["_id"]
                # Remove the custom info from the row
                row.pop("info")

                # Save the custom info to a string
                cust_info_payload = orjson.dumps(custom_info)

                custom_info_record = {
                    f"parents.{key}": value for key, value in row["parents"].items()
                }
                custom_info_record[f"parents.{container_type}"] = container_id
                custom_info_record["custom_info"] = cust_info_payload
                custom_info_file_list.append(custom_info_record)

        tmp_df = pd.DataFrame(custom_info_file_list)
        if self.tables.get("custom_info") is None:
            return pd.concat([empty_custom_info_df, tmp_df])
        else:
            return pd.concat([self.tables["custom_info"], tmp_df])

    def save_table_to_dataset(
        self, table: str, table_name: str, raw_list: list, table_columns: list = None
    ) -> None:
        """Save a table partition to the dataset directory.

        Args:
            table (str): The type of table.
            table_name (str): The name of the table.
            raw_list (list): The list of dictionaries to save.
            table_columns (list, optional): The final columns of the table. Defaults to None.
        """
        # Ensure we have all the columns in the table
        if not table_columns:
            default_table_schema = SNAPSHOT_MAPPINGS[table]["schema"]
            table_columns = self.get_table_control_columns(default_table_schema)

        table_df = pd.json_normalize(raw_list)

        # Rename the columns to match the schema
        field_mappings = SNAPSHOT_MAPPINGS[table]["field_mappings"]
        table_df = table_df.rename(columns=field_mappings)

        # Ensure all columns exist and are in the correct order...even if empty
        table_df = table_df.reindex(columns=table_df.columns.union(table_columns))
        table_df = table_df[table_columns]

        table_schema = SNAPSHOT_MAPPINGS[table]["schema"]
        table_schema = drop_schema_properties(table_schema, table_columns)
        self.dataset.tables[table_name] = table_schema

        save_schema(
            self.dataset._fs,
            self.dataset.paths.schemas_path,
            table_name,
            table_schema.model_dump(mode="json"),
        )

        # TODO: We may want to repartition the tables based on column values
        # NOTE: pyarrow can be used to write the parquet files with partitioning
        #       from an individual dataframe
        partition_name = table_df.iloc[0].get("id") if not table_df.empty else table

        table_df = enforce_field_types(table_schema, table_df, enforce=True)
        # NOTE: This allows for schema evolution
        save_pyarrow_table(
            self.dataset._fs,
            self.dataset.paths.tables_path,
            table_name,
            table_df,
        )

    def get_table_control_columns(self, default_table_schema: DataModel) -> list:
        """Get the retained columns of the table based on the control schema.

        The columns of the tables can be restricted down to the "required", but no
        further.

        Args:
            default_table_schema (DataModel): The default schema of the table.

        Returns:
            list: The columns of the table.
        """
        table = default_table_schema.id
        retained_columns = self.control_columns.get(table, [])
        default_properties = default_table_schema.properties.keys()
        retained_columns = validate_retained_columns(
            default_properties, retained_columns
        )

        # If the control columns are set, restrict the columns to the control columns
        if retained_columns and isinstance(retained_columns, list):
            required_columns = default_table_schema.required
            # Ensure the columns are returned in order
            results = [
                col
                for col in default_properties
                if (col in retained_columns) or (col in required_columns)
            ]

            return results
        # If the control columns are not set, return all the columns
        return list(default_table_schema.properties.keys())

    def load_tables_from_snapshot(self, snapshot_file_path: Path = None) -> None:
        """Load data from the latest snapshot of the dataset."""
        # Decompress the snapshot
        if not snapshot_file_path:
            snapshot_file_path = self.decompress_snapshot()
        conn = sqlite3.connect(snapshot_file_path)

        snapshot_tables = ["subject", "session", "acquisition", "file", "analysis"]

        # There is only one project record in the snapshot
        _, project_results = conn.execute("SELECT * FROM project").fetchone()

        project_dict = json.loads(project_results)

        self.tables["custom_info"] = self.extract_custom_info_from_container_records(
            [project_dict], "project"
        )

        # save the project record to a gzipped json file at the dataset level
        # TODO: Implement the display of the project record in the dataset UI
        with self.dataset._fs.open(
            self.dataset.paths.provenance_path / "project.json", "w", encoding="utf-8"
        ) as f:
            f.write(json.dumps(project_dict, default=str, indent=4))

        # Loop through the database tables and load them into the dataset object
        for table in snapshot_tables:
            table_name = SNAPSHOT_MAPPINGS[table]["table_name"]
            log.info(f"Loading {table} table...")

            # Iterate through the table in partition_size chunks
            for raw_df in pd.read_sql_query(
                f"SELECT * FROM {table}", conn, chunksize=self.partition_size
            ):
                # Convert the raw data to a list of dictionaries
                raw_list = [orjson.loads(row) for row in raw_df.data.values]

                # Extract the custom information from the container records
                self.tables["custom_info"] = (
                    self.extract_custom_info_from_container_records(
                        raw_list, container_type=table
                    )
                )

                self.save_table_to_dataset(table, table_name, raw_list)

                # Custom Information is a "hidden" table that is not displayed in the UI
                # It is used to store the custom information of the containers for later
                # extraction into tables for fast querying
                if self.tables["custom_info"].shape[0] >= self.partition_size:
                    self.tables["custom_info"] = save_custom_info_table(
                        self.dataset, self.tables["custom_info"]
                    )

        self.tables["custom_info"] = save_custom_info_table(
            self.dataset, self.tables["custom_info"]
        )

    def set_dataset_as_latest(self) -> None:
        """Set the dataset as the latest version."""
        # Save the dataset info to the project
        log.info("Setting dataset version as latest...")
        self.save_dataset_info()

        latest_version_path = self.dataset.paths.dataset_path / "latest"
        latest_version_json_path = (
            latest_version_path / "provenance" / "dataset_description.json"
        )

        # If the latest version dir and json file exist...and are distinct from the
        # current version, move them to the named directory
        if self.dataset._fs.exists(
            latest_version_json_path
        ) and self.dataset._fs.exists(latest_version_path):
            with self.dataset._fs.open(latest_version_json_path, "r") as f:
                latest_version_json = json.load(f)
                latest_version = latest_version_json.get("version")

                if latest_version == self.dataset.version:
                    log.info(
                        "Dataset already rendered in latest version for snapshot %s.",
                        self.dataset.version,
                    )
                    return
                else:
                    self.dataset._fs.mv(
                        str(latest_version_path),
                        str(
                            self.dataset.paths.dataset_path
                            / "versions"
                            / latest_version
                        ),
                        recursive=True,
                    )
        elif self.dataset._fs.exists(latest_version_path):
            self.dataset._fs.rm(str(latest_version_path), recursive=True)

        # Move the created dataset to the latest version dir and json file
        self.dataset._fs.mv(
            str(self.dataset.paths.version_path),
            str(latest_version_path),
            recursive=True,
        )
        self.dataset.setup_paths()
        self.save_dataset_info()
        self.dataset._fs.cp(
            str(self.dataset.paths.provenance_path / "dataset_description.json"),
            str(self.dataset.paths.dataset_path / "versions" / "latest_version.json"),
        )

    def render_dataset(
        self,
        parse_tabular_data: bool = POPULATE_TABULAR_DATA,
        parse_custom_info: bool = POPULATE_CUSTOM_INFO,
        remove_temp_files: bool = True,
        version_label: str = None,
        force_new: bool = False,
    ) -> Dataset | None:
        """Populate a dataset from a Flywheel project id.

        This function creates a dataset from a Flywheel project by creating and
        populating the following containers as tables from a snapshot:
        - Subjects
        - Sessions
        - Acquisitions
        - Analyses
        - Files

        Optionally, tabular data and custom information can be parsed into tables. As
        this can take a long time, it is disabled by default.

        If the version_label is not unique, the function will raise a ValueError. If the
        version_label is None, the version_id will be used.

        Args:
            project_id (str): The Flywheel project ID to create the dataset from.
            parse_tabular_files (bool, optional): Parse Tabular Files to tables . Defaults to POPULATE_TABULAR_DATA.
            parse_custom_info (bool, optional): Parse custom info to tables. Defaults to POPULATE_CUSTOM_INFO.
            remove_temp_files (bool, optional): Remove temp files after complete. Defaults to True.
            version_label (str, optional): The label for the version. Defaults to None.
            force_new (bool, optional): Force the creation of a new snapshot. Defaults to False.
        Returns:
            Path: The path to the dataset.
        """
        # TODO: Put checks to ensure that the project and storage have been set
        try:
            # Ensure that the new label is unique
            if version_label in [
                version.get("label") for version in self.dataset.list_versions()
            ]:
                raise ValueError("Version label must be unique.")

            self.version_label = version_label

            self.create_or_get_latest_snapshot(force_new=force_new)

            dataset_description_path = (
                self.dataset.paths.provenance_path / "dataset_description.json"
            )
            latest_version_path = (
                self.dataset.paths.dataset_path / "versions/latest_version.json"
            )
            latest_description_path = (
                self.dataset.paths.dataset_path
                / "latest/provenance"
                / "dataset_description.json"
            )

            # TODO: Turn this into a method of the dataset object
            if self.dataset._fs.exists(dataset_description_path):
                with self.dataset._fs.open(dataset_description_path, "r") as f:
                    dataset_description = json.load(f)
                    if dataset_description.get("version") == self.dataset.version:
                        log.info(
                            "Dataset already rendered for snapshot %s",
                            self.dataset.version,
                        )
                        return self.dataset
            elif self.dataset._fs.exists(
                latest_version_path
            ) and self.dataset._fs.exists(latest_description_path):
                with (
                    self.dataset._fs.open(latest_description_path, "r") as ldf,
                    self.dataset._fs.open(latest_version_path, "r") as lvf,
                ):
                    latest_dataset_description = json.load(ldf)
                    latest_version = json.load(lvf)

                    if (
                        latest_dataset_description.get("version")
                        == self.dataset.version
                    ) and (latest_version.get("version") == self.dataset.version):
                        log.info(
                            "Dataset already rendered in latest version for snapshot %s.",
                            self.dataset.version,
                        )
                        return self.dataset
            log.info(
                "Rendering dataset from snapshot %s, %s",
                self.dataset.version,
                self.dataset.version_label,
            )
            self.load_tables_from_snapshot()

            # Parse tabular data files only if specified
            if parse_tabular_data:
                log.info("Parsing tabular data...")
                tabular_file_table_builder = TabularFileTableBuilder(
                    self.dataset, self.sdk_client
                )
                tabular_file_table_builder.populate_from_tabular_data()

            # Parse custom information only if specified
            if parse_custom_info:
                # Search hidden "custom_info" table for file info with "qc" and "header"
                # tags at top level
                log.info("Parsing custom info...")
                custom_info_table_builder = CustomInfoTableBuilder(self.dataset)
                custom_info_table_builder.populate_from_custom_information()

            if remove_temp_files:
                log.info("Removing temp files...")
                try:
                    if self.dataset._fs.exists(
                        str(self.dataset.paths.files_cache_path)
                    ):
                        self.dataset._fs.rm(
                            str(self.dataset.paths.files_cache_path), recursive=True
                        )
                except Exception as e:
                    log.error("Error removing temp files.")
                    log.exception(e)

            self.set_dataset_as_latest()

            log.info("Dataset rendering complete.")

        except Exception as e:
            log.error("Error rendering snapshot.")
            log.exception(e)
            return None
        else:
            return self.dataset
