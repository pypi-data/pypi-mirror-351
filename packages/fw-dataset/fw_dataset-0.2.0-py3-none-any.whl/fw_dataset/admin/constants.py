import json
import os
from pathlib import Path

from ..models import DataModel

#      This should be replaced with a PATH that is set by an environment variable, a
#      cli parameter, or a configuration file.
DEFAULT_DATAHOME = Path.home() / "fw-ga4gh-drs-gateway-data"
DATAHOME = Path(os.environ.get("FW_DATA_HOME", DEFAULT_DATAHOME))

# TODO: The SECRET_KEY should be stored in an environment variable or configuration file
DEFAULT_SECRET_KEY = "your_secret_key"
SECRET_KEY = os.environ.get("FW_SECRET_KEY", DEFAULT_SECRET_KEY)

# ALLOWED_INSTANCES restricts the Flywheel instances that can be accessed by the
# gateway. If this is not set, the gateway will allow access to any Flywheel instance.
# This should be a list of Flywheel URIs.
# e.g. ALLOWED_INSTANCES = ["latest.sse.flywheel.io","trial.flywheel.io"]
DEFAULT_ALLOWED_INSTANCES = []
# FW_ALLOWED_INSTANCES should be a colon-separated list of Flywheel URIs
env_allowed_instances = os.environ.get("FW_ALLOWED_INSTANCES")
ALLOWED_INSTANCES = (
    env_allowed_instances.split(":")
    if env_allowed_instances
    and isinstance(env_allowed_instances, str)
    and env_allowed_instances != ""
    else DEFAULT_ALLOWED_INSTANCES
)

# The maximum number of items that can be returned in a single page of results
PAGINATION_LIMIT = os.environ.get("PAGINATION_LIMIT", 100)

# The maximum time to spend waiting for a snapshot to be created
SNAPSHOT_TIMEOUT = os.environ.get("SNAPSHOT_TIMEOUT", 60 * 30)  # 30 minutes

# The default behavior for populating from tabular data and custom information
POPULATE_TABULAR_DATA = os.environ.get("POPULATE_TABULAR_DATA", "false") == "true"
POPULATE_CUSTOM_INFO = os.environ.get("POPULATE_CUSTOM_INFO", "false") == "true"

# The default path to the schemas
DEFAULT_SCHEMAS_PATH = Path(__file__).parent / "default_container_schemas"

TIMESTAMP_PATTERN = (
    "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}+00:00$"
)

# TODO: Put all of the well-known container definitions in JSON files.
# TODO: flywheel.SubjectOutput.swagger_types may give us all of the fields we need
# NOTE: The fields in the swagger_types are not the same as the fields in the MongoDB

SUBJECT_SCHEMA_PATH = DEFAULT_SCHEMAS_PATH / "subjects.schema.json"
SUBJECT_SCHEMA = DataModel(**json.load(SUBJECT_SCHEMA_PATH.open("r")))

SESSION_SCHEMA_PATH = DEFAULT_SCHEMAS_PATH / "sessions.schema.json"
SESSION_SCHEMA = DataModel(**json.load(SESSION_SCHEMA_PATH.open("r")))

ACQUISITION_SCHEMA_PATH = DEFAULT_SCHEMAS_PATH / "acquisitions.schema.json"
ACQUISITION_SCHEMA = DataModel(**json.load(ACQUISITION_SCHEMA_PATH.open("r")))

ANALYSIS_SCHEMA_PATH = DEFAULT_SCHEMAS_PATH / "analyses.schema.json"
ANALYSIS_SCHEMA = DataModel(**json.load(ANALYSIS_SCHEMA_PATH.open("r")))

FILE_SCHEMA_PATH = DEFAULT_SCHEMAS_PATH / "files.schema.json"
FILE_SCHEMA = DataModel(**json.load(FILE_SCHEMA_PATH.open("r")))

TABULAR_DATA_SCHEMA = DataModel(
    **{
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "tabular_rasa",
        "description": "",
        "properties": {
            "parents.group": {
                "description": "The group that the file belongs to",
                "type": "string",
            },
            "parents.project": {
                "description": "The project that the file belongs to",
                "type": "string",
            },
            "parents.subject": {
                "description": "The subject that the file belongs to",
                "type": "string",
            },
            "parents.session": {
                "description": "The session that the file belongs to",
                "type": "string",
            },
            "parents.acquisition": {
                "description": "The acquisition that the file belongs to",
                "type": "string",
            },
            "parents.analysis": {
                "description": "The analysis that the file belongs to",
                "type": "string",
            },
            "parents.file": {
                "description": "The file id that the data of the row comes from",
                "type": "string",
            },
        },
        "required": [
            "parents.group",
            "parents.project",
            "parents.subject",
            "parents.session",
            "parents.acquisition",
            "parents.analysis",
            "parents.file",
        ],
        "type": "object",
    }
)

INFO_DICT = TABULAR_DATA_SCHEMA.model_dump()
INFO_DICT["properties"].update(
    {
        "custom_info": {
            "description": "Custom Information for container",
            "type": "string",
        }
    }
)
INFO_DICT["required"].append("custom_info")
INFO_DICT["$id"] = "custom_info"
INFO_SCHEMA = DataModel(**INFO_DICT)


TABLES = [
    {"id": "subjects", "name": "Subjects", "schema": SUBJECT_SCHEMA},
    {"id": "sessions", "name": "Sessions", "schema": SESSION_SCHEMA},
    {"id": "acquisitions", "name": "Acquisitions", "schema": ACQUISITION_SCHEMA},
    {"id": "analyses", "name": "Analyses", "schema": ANALYSIS_SCHEMA},
    {"id": "files", "name": "Files", "schema": FILE_SCHEMA},
]

# The mapping of the snapshot name to the table name, field mappings, and schema
# NOTE: snapshot table names and fields differ from the container names and properties
SNAPSHOT_MAPPINGS = {
    "subject": {
        "table_name": "subjects",
        "field_mappings": {"_id": "id"},
        "schema": SUBJECT_SCHEMA,
    },
    "session": {
        "table_name": "sessions",
        "field_mappings": {"_id": "id"},
        "schema": SESSION_SCHEMA,
    },
    "acquisition": {
        "table_name": "acquisitions",
        "field_mappings": {"_id": "id"},
        "schema": ACQUISITION_SCHEMA,
    },
    "analysis": {
        "table_name": "analyses",
        "field_mappings": {"_id": "id"},
        "schema": ANALYSIS_SCHEMA,
    },
    "file": {
        "table_name": "files",
        "field_mappings": {
            "_id.file_id": "file_id",
            "_id.version": "version",
            "uuid": "id",
        },
        "schema": FILE_SCHEMA,
    },
}
