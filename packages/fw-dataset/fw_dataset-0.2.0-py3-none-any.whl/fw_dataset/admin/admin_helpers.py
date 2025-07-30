"""Helper functions for the admin module."""

import csv
import json
import logging
import re
import uuid
import warnings
from ast import literal_eval as safe_eval
from copy import deepcopy
from pathlib import Path
from types import NoneType
from typing import Dict, Union

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from deepdiff import DeepDiff
from duckdb import DuckDBPyConnection
from flywheel.models.mixins import ContainerBase as Container
from fsspec import AbstractFileSystem
from pandas import StringDtype
from pandas.core.dtypes.dtypes import DatetimeTZDtype
from pyarrow import dataset as ds

from ..fw_dataset import Dataset
from ..models import DataModel
from .constants import TABULAR_DATA_SCHEMA

warnings.filterwarnings(
    "ignore", message="Passing 'use_legacy_dataset' is deprecated as of pyarrow 15.0.0"
)

log = logging.getLogger(__name__)

# Explicitly define NA Types
NAType = type(pd.NA)
NATType = type(pd.NaT)

# Dictionary to map Pandas data types to JSON schema types
TYPE_TO_SCHEMA = {
    "string": "string",
    "float64": "number",
    "int64": "integer",
    "bool": "boolean",
    "list": "array",
    "object": "string",
    "datetime64[ns, tzutc()]": "datetime64[ns]",
}

# Dictionary to map JSON schema types to default values
TYPE_DEFAULTS = {
    "string": "",
    "number": 0.0,
    "integer": 0,
    "boolean": False,
    "object": {},
    "array": [],
}

# Dictionary to map JSON schema types to Pandas types
# Used for conversion of values to enforce schema types
SCHEMA_TO_TYPE = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}

# Dictionary to map JSON schema types to Pandas types
# Used for the creation of a template DataFrame
SCHEMA_TO_PD_TYPE = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "object": np.dtype("O"),
    "array": np.dtype("O"),
}


def register_arrow_virtual_table(
    conn: DuckDBPyConnection,
    filesystem: AbstractFileSystem,
    table_id: str,
    table_path: Path,
    file_format: str = "parquet",
) -> None:
    """Register an arrow table as a virtual table in the database.

    data_path can be a directory containing multiple parquet files or a single parquet
    file.

    Args:
        conn (DuckDBPyConnection): The connection to the DuckDB database
        table_id (str): The table id
        table_path (Path): The path to the parquet file(s)
        file_format (str): The file format of the data. Defaults to "parquet".
    """
    existing_tables = conn.execute("SHOW TABLES").fetchdf()
    existing_tables = existing_tables["name"].tolist()
    if table_id not in existing_tables:
        dataset = ds.dataset(str(table_path), format=file_format, filesystem=filesystem)
        scanner = ds.Scanner.from_dataset(dataset)
        conn.register(table_id, scanner)


def validate_retained_columns(schema_properties: list, retained_columns: list) -> list:
    """Validate retained columns to ensure they are in the schema properties.

    This ensures that the columns to keep are in the schema properties. If they are not,
    the missing columns are omitted from the retained columns.

    Args:
        schema_properties (list): The full set of schema properties.
        retained_columns (list): The list of columns to keep.

    Returns:
        list: A list of columns to keep that have been validated against the schema.
    """
    if not (set(schema_properties).issuperset(set(retained_columns))):
        # NOTE: If the control columns are not in the schema, they are omitted
        missing_columns = set(retained_columns) - set(schema_properties)
        log.warning(f"Columns {missing_columns} are not in the schema properties.")
        # Remove the missing columns from the retained columns
        retained_columns = list(set(retained_columns) - missing_columns)

    return retained_columns


def drop_schema_properties(schema: DataModel, retained_columns: list) -> dict:
    """Drop schema properties that are not in the columns list and are not required.

    Args:
        schema (DataModel): The schema to drop properties from.
        retained_columns (list): The list of columns to keep.

    Returns:
        DataModel: The schema with the properties dropped.
    """
    new_schema = deepcopy(schema)
    schema_properties = new_schema.properties
    required_columns = schema.required
    retained_columns = validate_retained_columns(
        schema_properties.keys(), retained_columns
    )

    # If the retained columns are non-empty, drop the columns that are not in the list
    if retained_columns:
        for key in list(schema_properties.keys()):
            if (key not in retained_columns) and (key not in required_columns):
                schema_properties.pop(key)

    return new_schema


def save_schema(
    filesystem: AbstractFileSystem,
    schemas_path: Path,
    schema_name: str,
    schema: dict,
    overwrite: bool = False,
) -> None:
    """Save schema to the dataset directory.

    Args:
        filesystem (AbstractFileSystem): The filesystem object to use.
        schemas_path (Path): The path to the dataset schemas.
        schema_key (str): The key of the schema.
        schema (dict): The schema to save.
        overwrite (bool, optional): Overwrite the schema if it exists. Defaults to False.
    """
    schema_path = schemas_path / f"{schema_name}.schema.json"
    filesystem.makedirs(str(schema_path.parent), exist_ok=True)
    if not filesystem.exists(str(schema_path)) or overwrite:
        with filesystem.open(str(schema_path), "w") as f:
            json.dump(
                schema,
                f,
                indent=4,
                default=str,
            )


def save_table(
    filesystem: AbstractFileSystem,
    tables_path: Path,
    table_name,
    table_df,
    partition=None,
) -> None:
    """Save a table to the dataset directory.

    # TODO: Create a way to update a table, append, or overwrite it.
    # TODO: This is where we can save the table_df with field partitions.

    Args:
        filesystem (AbstractFileSystem): The filesystem object to use.
        tables_path (Path): The path to the tables of the dataset.
        table_name (str): The name of the table.
        table_df (pd.DataFrame): The dataframe to save.
        partition (str, optional): The partition of the table. Defaults to None.
    """
    table_path = f"{tables_path}/{table_name}"

    filesystem.makedirs(table_path, exist_ok=True)
    if partition:
        table_path_file = f"{table_path}/{partition}.parquet"
    else:
        table_path_file = f"{table_path}/{table_name}.parquet"

    if not filesystem.exists(table_path_file):
        with filesystem.open(table_path_file, "wb") as f:
            table_df.to_parquet(f)


def is_column_of_list_type(series: pd.Series, element_type: type) -> bool:
    """
    Check if non-null pandas Series values are lists or ndarrays of given element type.

    Args:
        series (pd.Series): The column to check.
        element_type (type): The expected type of elements in the lists.

    Returns:
        bool: True if all non-null values are lists containing only the specified type, False otherwise.
    """
    non_null_values = series.dropna()
    if non_null_values.empty:
        return False  # No data to verify

    return all(
        isinstance(val, (list, np.ndarray))
        and all(isinstance(x, element_type) for x in val)
        for val in non_null_values
    )


def infer_pyarrow_schema(table_df: pd.DataFrame) -> pa.Schema:
    """Infer a PyArrow schema from a pandas DataFrame.

    This ensures that lists of strings are stored correctly as `list<string>`.

    Args:
        table_df (pd.DataFrame): The DataFrame to infer the schema from.

    Returns:
        pa.Schema: The inferred PyArrow schema.
    """
    fields = []
    convert_to_strings = (StringDtype, DatetimeTZDtype)
    for col, dtype in table_df.dtypes.items():
        if is_column_of_list_type(table_df[col], str):  # Detect list<string>
            # Ensure the column is properly formatted as a list of strings
            # This prevents concatenation of strings when saving to Parquet
            fields.append(
                pa.field(col, pa.list_(pa.string()), nullable=True)
            )  # Define list<string>
        elif dtype in ("object", "string") or isinstance(dtype, convert_to_strings):
            table_df[col] = (
                table_df[col]
                .replace({"None": None, "nan": None, "": None})
                .astype("string")
            )
            fields.append(
                pa.field(col, pa.string(), nullable=True)
            )  # Convert generic objects to strings
        else:
            fields.append(
                pa.field(col, pa.from_numpy_dtype(dtype), nullable=True)
            )  # Handle other types

    return pa.schema(fields)


def save_pyarrow_table(
    filesystem: AbstractFileSystem,
    tables_path: Path,
    table_name: str,
    table_df: pd.DataFrame,
    partition_cols: list | None = None,
) -> None:
    """Save a table to the dataset directory with a pyarrow table.

    This function enables the saving of tables with partitions and schema evolution.

    NOTE: Introducing partitioning on columns increases the size of the dataset (e.g.
    22 Mb w/o partitioning v.s. 2.0 Gb partitioning on subject_id and session_id).

    Schema evolution is the ability to add new columns to a table without breaking
    existing queries.

    Args:
        filesystem (AbstractFileSystem): The filesystem object to use.
        tables_path (Path): The path to the tables of the dataset.
        table_name (str): The name of the table.
        table_df (pd.DataFrame): The dataframe to save.
        partition_cols (list, optional): The columns of the dataframe to partition on. Defaults to None.
    """
    table_path = f"{tables_path}/{table_name}"

    # Create the "directory" structure
    filesystem.makedirs(table_path, exist_ok=True)

    # Ensure partition columns exist in the DataFrame
    if partition_cols:
        for col in partition_cols:
            if col not in table_df.columns:
                table_df[col] = pd.NA  # Add missing partition columns

    # Infer the schema from the DataFrame
    schema = infer_pyarrow_schema(table_df)

    table = pa.Table.from_pandas(table_df, schema=schema)
    # Handle empty DataFrame
    if table_df.empty:
        # If a table with defined columns is empty
        table_file_path = f"{table_path}/{table_name}.parquet"
        # This method is used to write an empty table to a parquet file
        pq.write_table(table, where=table_file_path, filesystem=filesystem)
    else:
        # The table dataframe is not empty
        # Write to Parquet dataset
        pq.write_to_dataset(
            table,
            root_path=table_path,
            existing_data_behavior="overwrite_or_ignore",
            partition_cols=partition_cols,
            filesystem=filesystem,
        )


def convert_to_bool(value, default):
    """Convert a value to boolean with consistent rules.

    Args:
        value: Value to convert.
        default: The default value if the conversion fails.

    Returns:
        bool, None: The converted value.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        try:
            value = bool(value)
        except ValueError:
            log.debug("Invalid bool value %s", value)
            return default if (default is None) or isinstance(default, bool) else False
        return value

    true_values = {"y", "yes", "t", "true", "1"}
    false_values = {"n", "no", "f", "false", "0"}

    str_value = str(value).lower().strip()

    if str_value in true_values:
        return True
    if str_value in false_values:
        return False

    return default if (default is None) or isinstance(default, bool) else False


def convert_with_default(value, dtype, default):
    """Convert a value to a type with a default fallback.

    Args:
        value: Value to convert.
        dtype: The type to convert the value to.
        default: The default value if the conversion fails.

    Returns:
        variable_type: The converted or default value
    """
    # Handle pandas NA and None values safely
    try:
        if isinstance(value, (NAType, NATType, NoneType)):
            return default
    except Exception:
        # If check fails, continue processing
        pass

    if dtype is bool:
        return convert_to_bool(value, default)

    # If the value is already the correct type, return it directly
    if isinstance(value, dtype):
        return value

    # Handle special cases for different types
    try:
        if dtype is str:
            return str(value)

        elif dtype is list:
            # Handle list conversion carefully
            if isinstance(value, np.ndarray):
                # Convert numpy arrays to list
                return value.tolist()
            elif isinstance(value, pd.Series):
                # Convert pandas series to list
                return value.tolist()
            elif isinstance(value, str):
                # If it's a string that looks like a list, try to convert it
                if value.startswith("[") and value.endswith("]"):
                    try:
                        return safe_eval(value)
                    except (ValueError, SyntaxError):
                        # If it can't be evaluated as a list, wrap the string in a list
                        return default
                else:
                    # Return default value
                    return default
            else:
                # For any other type, try to convert to list
                try:
                    return list(value)
                except:
                    # If conversion fails, return default
                    return default

        elif dtype is dict:
            # Handle dictionary conversion carefully
            if isinstance(value, str):
                if value.startswith("{") and value.endswith("}"):
                    try:
                        return safe_eval(value)
                    except (ValueError, SyntaxError):
                        # If it can't be evaluated as a dict, return default
                        return default
                else:
                    # Not a dict-like string
                    return default
            else:
                # Try to convert to dict if possible
                try:
                    return dict(value)
                except:
                    return default
        else:
            # For other types, try direct conversion
            return dtype(value)
    except (ValueError, TypeError):
        return default


def get_schema_type(property_def):
    """Extract the primary type from a schema property definition.

    Args:
        property_def (dict): The property definition from the schema.

    Returns:
        str: The primary type of the property.
    """
    prop_type = property_def["type"]
    # If the `"type": ["null", "string"]` is a nullable type
    if isinstance(prop_type, list):
        # Get first non-null type
        return next(t for t in prop_type if t != "null")
    return prop_type


def get_default_value(property_def, schema_type):
    """Get default value using a clear precedence.

    Args:
        property_def (dict): The property definition from the schema.
        schema_type (str): The type of the property.

    Returns:
        any: The default value for the property.
    """
    if "default" in property_def:
        return property_def["default"]
    if isinstance(property_def["type"], list) and "null" in property_def["type"]:
        return None
    return TYPE_DEFAULTS.get(schema_type, None)


def create_template_df_from_schema(schema: DataModel) -> pd.DataFrame:
    """Create a template dataframe from a schema.

    This preserves the order of the expected columns

    Args:
        schema (DataModel): Schema for the template dataframe.

    Returns:
        pd.DataFrame: Resultant template dataframe.
    """
    template_columns = list(schema.properties.keys())
    # Convert schema types to pandas types
    template_types = [get_schema_type(prop) for prop in schema.properties.values()]
    template_types = [SCHEMA_TO_PD_TYPE.get(prop, str) for prop in template_types]
    template_df = pd.DataFrame(
        {col: pd.Series(dtype=dt) for col, dt in zip(template_columns, template_types)}
    )
    return template_df


def enforce_field_types(
    schema: DataModel, table_df: pd.DataFrame, enforce: bool = False
) -> pd.DataFrame:
    """Use a schema to enforce field types on a table dataframe.

    When enforce is True, the field types are enforced even if they are not different.

    A dataframe is returned with only the columns in the schema.

    If the columns are missing in the dataframe, the columns are added with the default
    value.

    Default values are determined in the following order:

    1. The default value in the schema (e.g. "default": {type-specific value})
    2. A `None` value if the type is nullable (e.g. "type": ["null", "string"])
    3. The type-specific default value (e.g. "type": "string" -> "default": "")

    Args:
        schema (DataModel): The schema to enforce on the table dataframe.
        table_df (pandas.Dataframe): The table dataframe to enforce the schema on.
        enforce (bool, optional): Enforce the schema on the table dataframe. Defaults to False.

    Returns:
        pandas.Dataframe: The table dataframe with enforced field types.
    """
    # Set up a template DataFrame with the expected columns and types
    template_df = create_template_df_from_schema(schema)

    if table_df.empty:
        return template_df

    # Ensure we have a dataframe with all of the required columns and eliminate any not
    # in the schema properties
    result_df = pd.concat([template_df, table_df], ignore_index=True)

    for prop_name, prop_def in schema.properties.items():
        schema_type = get_schema_type(prop_def)
        default_value = get_default_value(prop_def, schema_type)
        desired_type = SCHEMA_TO_TYPE[schema_type]

        # Add missing columns with default values
        if prop_name not in result_df.columns:
            result_df[prop_name] = default_value
            continue

        # Convert column if type doesn't match or enforce is True
        current_type = str(result_df[prop_name].dtype.name)
        if enforce or TYPE_TO_SCHEMA.get(current_type, "string") != schema_type:
            try:
                result_df[prop_name] = result_df[prop_name].apply(
                    lambda x,
                    dtype=desired_type,
                    default=default_value: convert_with_default(
                        x, desired_type, default
                    )
                )
            except Exception as e:
                log.error(
                    "Error enforcing field types for property %s: %s", prop_name, e
                )

    return result_df[schema.properties.keys()]


def get_delimiter(filesystem, file_path, bytes_read=40960) -> str:
    """A function to get the delimiter of a csv file

    Args:
        file_path (Pathlike): The path to the file
        bytes (int, optional): The number of bytes to read. Defaults to 40960.

    Returns:
        str: The delimiter of the csv file
    """
    sniffer = csv.Sniffer()
    data = filesystem.open(file_path, "r", encoding="utf-8").read(bytes_read)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter


def sanitize_table_name(table_name) -> str:
    """Sanitize table names to conform to GA4GH DataConnect requirements.

    Args:
        table_name (str): The table name to sanitize.

    Returns:
        str: The sanitized table name.
    """
    valid_pattern = re.compile(r"^[a-z](?:[a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)?)*$")
    # Replace uppercase letters with lowercase
    table_name = table_name.lower()

    # Replace prohibited characters with underscore
    prohibited_chars = r'[!@#$%^&*()\-+=~`{}[\]|:;"\'<>,?\/\.\s]'
    table_name = re.sub(prohibited_chars, "_", table_name)

    # Replace digits following a "." with an underscore
    table_name = re.sub(r"\.(?=\d)", "._", table_name)

    # Remove leading invalid characters until a valid character is found
    while not valid_pattern.match(table_name):
        table_name = table_name[1:]
        if len(table_name) == 0:
            uuid_part = str(uuid.uuid4())[-12:]
            table_name = f"table_{uuid_part}"

    return table_name


def add_parent_info(table_df, fw_file) -> pd.DataFrame:
    """Ensure that the parent information is added to the table dataframe.

    This is intended to be used with the tabular data schema and the custom
    info schema.

    Args:
        table_df (pandas.Dataframe): Dataframe to add parent information to.
        fw_file (dict): File dictionary from the Flywheel SDK to use as a source.

    Returns:
        pandas.Dataframe: Dataframe with parent information added.
    """
    # Get existing columns
    table_columns = list(table_df.columns)

    parent_attributes = TABULAR_DATA_SCHEMA.required
    for attr in parent_attributes:
        attr_split = attr.split(".")
        sub_attr = attr_split[1]
        # Add the parent information to the table
        if sub_attr != "file":
            table_df[attr] = fw_file[attr_split[0]][sub_attr]
        # Else add the "parents.file" information to the table
        else:
            table_df[attr] = fw_file["file_id"]

        # Remove the attribute from the list of columns
        if attr in table_columns:
            table_columns.remove(attr)

    # Move the identifying attributes to the front
    table_columns = parent_attributes + table_columns
    table_df = table_df[table_columns]

    return table_df


def get_table_schema(filesystem=None, file_path=None, table_df=None, schema=None):
    """A function to get the schema of a csv file or dataframe.

    Open a csv file and read the first 1000 rows to estimate the data types of the
    columns. If we are given a DataFrame, we can use that to estimate the schema.
    A schema can be provided as a starting point.

    Args:
        filesystem (AbstractFileSystem, optional): The filesystem object to use. Defaults to None.
        file_path (Pathlike, optional): Path to a tabular data file. Defaults to None.
        table_df (pandas.DataFrame, optional): Populated DataFrame. Defaults to None.
        schema (dict, optional): The schema to use as template. Defaults to None.

    Returns:
        dict: The schema of the csv file/dataframe.
    """
    if file_path is None and table_df is None:
        raise ValueError("Either file_path or table_df must be provided.")

    if file_path and filesystem.exists(file_path):
        try:
            # Get the delimiter of the file
            delimiter = get_delimiter(filesystem, file_path)
            # Read the first 1000 rows of the file to estimate the data types
            # TODO: Other "tabular data" types need to be supported. CSV is the only one
            # currently supported.
            table_df = pd.read_csv(
                filesystem.open(file_path), delimiter=delimiter, nrows=1000, comment="#"
            )
        except Exception as e:
            log.exception(f"Error reading file: {file_path}")
            raise ValueError("Error reading file.") from e
    elif table_df is None:
        raise ValueError("Either file_path or table_df must be provided.")

    # If a schema is not provided, use the tabular data schema as a starting point
    if not schema:
        schema = TABULAR_DATA_SCHEMA.model_dump(mode="json")

    for col in table_df.columns:
        # TODO: This location is a good place to check and enforce the type of the
        # column
        # If the column is in the schema, preserve the entry
        if col not in schema["properties"].keys():
            schema["properties"][col] = {
                "type": TYPE_TO_SCHEMA[str(table_df[col].dtype)],
                "description": "",
            }
            schema["required"].append(col)

    return schema


def match_table_schema(matched_schemas: dict, schema_to_match: dict) -> str | None:
    """Match a schema to a list of schemas.

    NOTE: Eventually, scan the columns of the table and infer the data
    type of each column. Enforce a numeric type if the column is numeric,
    a string type if the column is a string, and a boolean type if the column is a
    boolean.

    TODO: This is the function to update with AI-driven schema matching.

    Args:
        schemas (dict): The list of schemas to match against
        schema_to_match (dict): The schema to match

    Returns:
        string: The key of the matched schema or None
    """
    for k, schema in matched_schemas.items():
        # TODO: a better matching protocol here
        ddiff = DeepDiff(
            schema_to_match["properties"],
            schema["properties"],
            ignore_order=True,
            threshold_to_diff_deeper=0,
        )
        if not ddiff:
            return k
        else:
            keys = [
                "dictionary_item_added",
                "dictionary_item_removed",
                "values_changed",
            ]
            num_diff = sum([len(ddiff[key]) for key in keys if ddiff.get(key)])
            # If the number of differences is less than 10% of the number of columns
            # in the schema, then consider the schemas to be the same
            # TODO: Make this a configurable parameter
            if num_diff / len(schema["properties"]) < 0.1:
                return k
    return None


def get_container_path(container_record: Union[Dict, Container]) -> Path:
    """Get the path of a container for saving files and info.

    Args:
        container_record (dict|Container): The container record to get the path from.

    Returns:
        Pathlike: The parent path of the container.

    Raises:
        ValueError: If the container_record is not a dict or a Container object.
    """
    if not isinstance(container_record, (Dict, Container)):
        raise ValueError("container_record must be a dict or a Container object.")

    container_path = Path(".")
    for parent in [
        "group",
        "project",
        "subject",
        "session",
        "acquisition",
        "analysis",
    ]:
        if container_record.get("parents") and container_record.get("parents", {}).get(
            parent
        ):
            container_path /= container_record["parents"][parent]

    if isinstance(container_record, Container):
        container_id = container_record.id
    elif isinstance(container_record, Dict):
        container_id = container_record["id"]

    # Always add the container id
    container_path /= container_id

    return container_path


def quote_identifier(identifier: str) -> str:
    """
    Safely quote a SQL identifier to prevent SQL injection.

    Args:
        identifier (str): The identifier to quote

    Returns:
        str: A safely quoted identifier
    """
    # Remove any null bytes
    clean_identifier = identifier.replace("\0", "")
    # Double any quotes and wrap in quotes
    return '"{}"'.format(clean_identifier.replace('"', '""'))


def count_table_rows(conn: DuckDBPyConnection, table_name: str) -> int:
    """
    Safely count rows in a table using parameterized queries.

    Args:
        conn (DuckDBPyConnection): DuckDB connection
        table_name (str): Name of the table

    Returns:
        int: Number of rows in the table
    """
    return conn.execute('SELECT COUNT(*) FROM "{}"', [table_name]).fetchone()[0]


def validate_dataset_table(duckdb_conn, filesystem, dataset, table_name) -> bool:
    """Validate a dataset table.

    Examines the dataset path, table path, and the table itself to ensure that the table
    is valid and non-empty.

    Args:
        duckdb_conn (duckdb.Connection): The DuckDB connection to use.
        filesystem (AbstractFileSystem): The filesystem object to use.
        dataset (Dataset): The Dataset Object.
        table_name (str): The name of the table to validate.

    Returns:
        bool: True if the table is valid, False otherwise.
    """
    # Validate table_name format
    if not isinstance(table_name, str) or not table_name.strip():
        log.error("Invalid table name")
        return False

    # Sanitize table name using existing function
    safe_table_name = sanitize_table_name(table_name)

    # Ensure the dataset path exists
    dataset_path = dataset.paths.dataset_path
    if not filesystem.exists(dataset_path):
        log.error(f"Dataset path {dataset_path} does not exist.")
        return False

    table_path = dataset.paths.tables_path / safe_table_name
    if not filesystem.exists(table_path):
        log.error(f'The "{safe_table_name}" table does not exist: {table_path}')
        return False

    try:
        register_arrow_virtual_table(
            duckdb_conn, filesystem, safe_table_name, table_path
        )

        # Use the dedicated counting function
        row_count = count_table_rows(duckdb_conn, safe_table_name)
        return row_count > 0

    except Exception as e:
        log.error(f'Error validating table "{safe_table_name}": {e}')
        return False


def save_custom_info_table(
    dataset: Dataset, custom_info_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Save a custom information table partition to the specified dataset path.

    Args:
        dataset (Dataset): The dataset object.
        custom_info_df (pd.DataFrame): The custom information table to be saved.
    Returns:
        pd.DataFrame: An empty DataFrame with the same columns as the custom_info_df.
    """
    if not custom_info_df.empty:
        save_pyarrow_table(
            dataset._fs, dataset.paths.tables_path, "custom_info", custom_info_df
        )

    return pd.DataFrame(columns=custom_info_df.columns)
