import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Field

# NOTE: The following models are based on the GA4GH Data Connect API specification.
#       They are reused and adapted for the purposes of the Flywheel Dataset Client.

# Suppress specific warning related to shadowing
warnings.filterwarnings(
    "ignore",
    message='Field name "schema" in "DataModel" shadows an attribute in parent "BaseModel"',
)


class Error(BaseModel):
    """Error object"""

    source: Optional[str]
    title: str
    detail: Optional[str]


class ErrorList(BaseModel):
    """List of errors encountered"""

    items: List[Error]


class DataModel(BaseModel):
    """Data Model describe attributes of Tables.

    The `properties` field is a dictionary where the keys are the names of the columns

    The `required` field is a list of the names of the columns that are required to be
    present in the data.

    The Data Model format follows JSON-Schema Draft 7.
    """

    schema: AnyUrl = Field(
        default="http://json-schema.org/draft-07/schema#", alias="$schema"
    )
    id: Optional[str] = Field(..., alias="$id")
    description: Optional[str] = ""
    properties: Dict[str, Any] = {}
    required: List[str] = []
    type: str = "object"

    class Config:
        populate_by_name: bool = True


class Table(BaseModel):
    """Uniquely identifies a table within this Data Connect service.

    Table names should be human-readable and will typically (but not necessarily)
    be split into two or three parts separated by a dot (`.`).
    """

    name: str
    description: str = ""
    data_model: DataModel
    errors: Optional[ErrorList] = None


class DatasetPaths(BaseModel):
    """Paths for a dataset."""

    root_path: Path = None
    dataset_path: Path = None
    version_path: Path = None
    schemas_path: Path = None
    tables_path: Path = None
    provenance_path: Path = None
    files_cache_path: Path = None
