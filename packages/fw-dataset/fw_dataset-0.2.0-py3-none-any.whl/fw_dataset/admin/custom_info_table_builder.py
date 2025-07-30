"""This module contains CustomInfoTableBuilder class for building tables from custom info.

The CustomInfoTableBuilder class is used to build parquet tables from a select set of
custom information keys. These keys are currently restricted to

{
    "header": {
        "dicom": {...},
        "...": {...},
    }
    "qc": {...}
}

These keys are expected to be present in the custom information of the DICOM files in
a Flywheel project. They have a well-defined schema that is infered and enforced on the
tables built from the custom information.

This class expects a dataset to be populated with the primary tables
(e.g. `subjects`, `sessions`, `acquisitions`, and `files`) and the hidden "custom_info"
table.

As this can be both time and resource-intensive, it is recommended to run this process
in a separate script or as a background task.
"""

import copy
import logging

import duckdb
import orjson as json
import pandas as pd

from ..fw_dataset import Dataset
from .admin_helpers import (
    get_table_schema,
    sanitize_table_name,
    save_pyarrow_table,
    save_schema,
    validate_dataset_table,
)

log = logging.getLogger(__name__)


class CustomInfoTableBuilder:
    """A class to build parquet tables from custom information in a Flywheel project."""

    def __init__(self, dataset: Dataset):
        """Initialize the CustomInfoTableBuilder class.

        Args:
            dataset_path (Path): The path to the dataset
        """
        self.dataset = dataset
        self.filesystem = dataset._fs

        # Establish the connection to the DuckDB database
        self.duckdb_conn = duckdb.connect()

        # Create a dictionary to host the tables to export
        # This will keep of track of the dictionary list, dataframe, and schema
        self.tables_to_export = {}

        # Here is a template record of the tables_to_export dictionary
        self.table_template = {
            "dict_list": [],  # list of dictionaries to be converted to a dataframe
            "df": pd.DataFrame(),  # an initialized dataframe
            "schema": {},  # The extracted schema from the dataframe
        }

    def cust_info_to_table_lists(
        self, cust_info_record, restrict_to_keys: list = None
    ) -> None:
        """Converts the custom information record to a list of dictionaries for each
        key in the custom information.

        TODO: Extend this method to handle more complex custom information schemas.

        Args:
            cust_info_record (dict): The custom information record to convert.
            restrict_to_keys (list, optional): A list of keys to restrict the conversion
                             to. If None, all keys are converted. Defaults to None.
        """
        # Record the parent info and the custom info of each row
        parent_info = {
            k: cust_info_record[k] for k in cust_info_record.keys() if "parents." in k
        }
        custom_info = json.loads(cust_info_record["custom_info"])

        # Iterate through the top level keys to filter the custom_info table
        for top_key in restrict_to_keys:
            if top_key in custom_info.keys():
                # Iterate through the secondary keys to filter the custom_info table
                for sec_key in custom_info[top_key].keys():
                    # Create a table key from the top and secondary keys
                    table_key = sanitize_table_name(f"{top_key}_{sec_key}")
                    # if the table_key is not in the table_to_export dictionary
                    # create a new entry with the dict_list, df, and schema keys
                    if table_key not in self.tables_to_export.keys():
                        self.tables_to_export[table_key] = copy.deepcopy(
                            self.table_template
                        )

                    # record the parent info and the custom info of each row
                    export_info = copy.deepcopy(parent_info)
                    export_info.update(custom_info[top_key][sec_key])
                    self.tables_to_export[table_key]["dict_list"].append(export_info)

    def export_table_lists_to_parquet_datasets(self):
        """Export the accumulated tables to the dataset directory as parquet tables."""

        # TODO: Throw errors and catch them in the calling function
        # TODO: This is a function that could be more generalized and moved to a helper
        # NOTE: DICOM Tags are not guaranteed to be consistent across all files.
        #       E.g. WindowCenter and WindowWidth can be a list or a single value.
        #       This can cause issues when converting to a dataframe.

        # Iterate through the tables to export for each chunk
        for table_key, export_record in self.tables_to_export.items():
            log.info(f"Exporting {table_key} table to parquet partition...")

            # Create a dataframe from the dictionary list
            # the dataframe will be concatenated with the existing dataframe
            existing_df = export_record["df"]
            temp_df = pd.json_normalize(export_record["dict_list"])

            table_df = pd.concat([existing_df, temp_df], ignore_index=True)

            # Initialize or update JSON schema for the table
            table_schema = get_table_schema(
                self.filesystem, table_df=table_df, schema=export_record["schema"]
            )
            table_schema["id"] = table_key
            export_record["schema"] = table_schema

            # Save the dataframe to the dataset directory partitioned by parents
            save_pyarrow_table(
                self.filesystem, self.dataset.paths.tables_path, table_key, table_df
            )

            # Clear the dictionary list for the next chunk and create an empty
            # dataframe with the accumulated columns
            export_record["dict_list"] = []
            export_record["df"] = pd.DataFrame(columns=table_df.columns).astype(
                table_df.dtypes
            )

    def populate_from_custom_information(self) -> None:
        """Populate from custom information referred to in hidden "custom_info" table."""

        if not validate_dataset_table(
            self.duckdb_conn,
            self.filesystem,
            self.dataset,
            "custom_info",
        ):
            print("The dataset is not valid. Please initialize the dataset first.")
            return

        # set the top level keys to filter the custom_info table
        # The first level of keys beneath these will be used as tables (e.g.
        # "header_dicom")
        top_level_keys = ["header", "qc"]

        # Filter the custom_info table for custom information of files
        # TODO: Extend this to handle more complex custom information schemas of all
        # containers
        SQL = 'SELECT * FROM custom_info where "parents.file" IS NOT NULL'

        results = self.duckdb_conn.execute(SQL)

        log.info("Filtering custom information for files...")
        # Fetch the files in chunks to avoid memory issues
        # chuck size is given by duckdb.__standard_vector_size__ = 2048
        while (tab_files_df := results.fetch_df_chunk()).empty is False:
            # iterate through the filtered custom_information to collate the data
            for _, row in tab_files_df.iterrows():
                self.cust_info_to_table_lists(row, restrict_to_keys=top_level_keys)

            # Export the tables of each chunk to the dataset directory
            self.export_table_lists_to_parquet_datasets()

        # Iterate through all of the tables encountered and save the accumulated schema
        for schema_key, schema_record in self.tables_to_export.items():
            schema_to_save = schema_record["schema"]
            save_schema(
                self.filesystem,
                self.dataset.paths.schemas_path,
                schema_key,
                schema_to_save,
            )
        log.info("Custom information to tables conversion complete.")
