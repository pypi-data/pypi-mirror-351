import logging
import os

from flywheel import Client as SDKClient
from flywheel import Project
from fw_client import FWClient as APIClient

from .filesystem import FSType, _get_storage_credentials, get_fs_type
from .fw_dataset import Dataset

log = logging.getLogger(__name__)


class FWDatasetClient:
    """A Flywheel Dataset Client.

    The FWDatasetClient is a client for interacting with Flywheel datasets. It can be
    used to get a list of datasets in a Flywheel instance, get a dataset object from a
    dataset_id or a path to a dataset, and create a dataset object from an authenticated
    filesystem.
    """

    def __init__(self, api_key: str = None):
        """Initialize the FWDatasetClient.

        If no API key is provided, the client will attempt to infer the API key from the
        environment variables FW_HOSTNAME and FW_WS_API_KEY, if present.

        Args:
            api_key (str, optional): The Flywheel API key for the Flywheel instance.

        Raises:
            ValueError: If an API-Key is not provided or infered from the environment.
        """
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
        self.sdk_client = SDKClient(api_key)
        self.api_client = APIClient(api_key=api_key)

        # Exclude files and analyses to speed up endpoints
        self.api_client.headers["X-Accept-Feature"] += ",Slim-Containers,Exclude-Files"
        self.sdk_client.api_client.rest_client.session.headers["X-Accept-Feature"] = (
            "Slim-Containers,Exclude-Files"
        )

    def datasets(self):
        """Get all datasets in the Flywheel instance.

        Iterates through all projects in the Flywheel instance, checks for a dataset
        object in the project info blob, and creates a dataset object for each dataset.

        The dataset object is as follows:
        project.info = {
          "dataset": {
            "type": "s3",
            "bucket": "bucket_name",
            "prefix": "path/to/dataset",
            "storage_id": "storage_id",
          }

        Returns:
            list: A list of a dataset objects in the Flywheel instance.
        """
        datasets = []
        for project in self.api_client.get("/api/projects"):
            project = self.api_client.get(f"/api/projects/{project._id}")
            if project.info.get("dataset"):
                dataset = self.get_dataset(project=project)
                datasets.append(dataset)
        return datasets

    def get_dataset(
        self,
        dataset_id: str = None,
        path: str = None,
        project: Project = None,
        dataset_class=Dataset,
    ):
        """Get a dataset object from parameters or environment variable.

        If a dataset_id (project_id), project_path, project, or environment variable is
        set (FW_WS_PROJECT_ID), the dataset object is created from the dataset info in
        the project.

        Args:
            dataset_id (str, optional): Project ID. Defaults to None.
            path (str, optional): group/project path to dataset. Defaults to None.
            project (Project, optional): A Flywheel project object. Defaults to None.

        Raises:
            ValueError: If a project cannot be found to initialize the dataset.

        Returns:
            Dataset: A valid dataset object.
        """
        if dataset_id and not project:
            try:
                project = self.sdk_client.get_project(dataset_id)
            except Exception as e:
                raise ValueError(f"Dataset not found: {dataset_id}") from e
        elif path and not project:
            if path.startswith("fw://"):
                stripped_path = path.replace("fw://", "")
            else:
                stripped_path = path
            try:
                project = self.sdk_client.lookup(stripped_path)
            except Exception as e:
                raise ValueError(f"Dataset not found: {stripped_path}") from e
        elif os.environ.get("FW_WS_PROJECT_ID"):
            project = self.sdk_client.get(os.environ.get("FW_WS_PROJECT_ID"))
        elif not project:
            raise ValueError(
                "You must provide either a dataset_id or a path to a dataset"
            )

        # TODO: What if the project does not have a dataset?
        dataset_info = project.info.get("dataset")
        if not dataset_id and project:
            dataset_id = project._id

        dataset = dataset_class(
            id=dataset_id,
            name=project.label,
            description=project.description,
            dataset_info=dataset_info,
        )
        fs_type = get_fs_type(dataset_info.get("type"))
        if fs_type == FSType.LOCAL:
            credentials = None
        else:
            try:
                credentials = _get_storage_credentials(
                    self.api_client,
                    dataset_info.get("type"),
                    dataset_info.get("storage_id"),
                )
            except ValueError:
                log_msg = (
                    f"No credentials for dataset {dataset_id}, "
                    f"storage: {dataset_info.get('storage_id')}"
                )
                log.warning(log_msg)
                return

        dataset.set_filesystem(fs_type, credentials)
        dataset.setup_paths()

        return dataset

    @classmethod
    def get_dataset_from_filesystem(
        cls, fs_type: str, bucket: str, prefix: str, credentials: dict
    ) -> Dataset:
        """Create a dataset object from an authenticated filesystem.

        Filesystem Types are "s3", "gs", "az", "fs" (local).

        credentials must be a dictionary with a url key for the credential string in the
        following format for each filesystem type:
        {'url': 's3://{bucket}?access_key_id={access_key_id}&secret_access_key={secret_access_key}'}
        {'url': 'gs://{bucket}?application_credentials={
            "type": "service_account",
            "project_id": "{project_id}",
            "private_key_id": "{private_key_id}",
            "private_key": "{private_key}",
            "client_email": "{email}",
            "client_id": "{client_id}",
            "auth_uri":"{auth_uri}",
            "token_uri":"{token_uri}",
            "auth_provider_x509_cert_url":"{auth_provider_x509_cert_url}",
            "client_x509_cert_url":"{client_x509_cert_url}",
            "universe_domain": "googleapis.com"
            }'
        }
        {'url': 'az://{account_name}.blob.core.windows.net/{container}?access_key={access_key}'}

        Args:
            fs_type (str): The type of filesystem to use. Options are "s3", "gs", "az", "fs".
            bucket (str): The bucket, container, or root directory of the dataset.
            prefix (str): The path from the bucket to the dataset.
            credentials (dict): A dictionary with a url key for the credential string.

        Returns:
            Dataset: A dataset object.
        """
        return Dataset.get_dataset_from_filesystem(fs_type, bucket, prefix, credentials)
