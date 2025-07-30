import os
import json
import inspect

from datetime import datetime
from google.protobuf import timestamp_pb2

from fivetran_connector_sdk import constants
from fivetran_connector_sdk.constants import (
    JAVA_LONG_MAX_VALUE,
    TABLES,
)
from fivetran_connector_sdk.helpers import (
    get_renamed_table_name,
    get_renamed_column_name,
    print_library_log,
)
from fivetran_connector_sdk.logger import Logging
from fivetran_connector_sdk.protos import connector_sdk_pb2, common_pb2

class Operations:
    @staticmethod
    def upsert(table: str, data: dict) -> list[connector_sdk_pb2.UpdateResponse]:
        """Updates records with the same primary key if already present in the destination. Inserts new records if not already present in the destination.

        Args:
            table (str): The name of the table.
            data (dict): The data to upsert.

        Returns:
            list[connector_sdk_pb2.UpdateResponse]: A list of update responses.
        """
        if constants.DEBUGGING:
            _yield_check(inspect.stack())

        responses = []

        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        if not columns:
            for field in data.keys():
                field_name = get_renamed_column_name(field)
                columns[field_name] = common_pb2.Column(
                    name=field_name, type=common_pb2.DataType.UNSPECIFIED, primary_key=False)
            new_table = common_pb2.Table(name=table, columns=columns.values())
            TABLES[table] = new_table

        mapped_data = _map_data_to_columns(data, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.UPSERT,
            data=mapped_data
        )

        responses.append(
            connector_sdk_pb2.UpdateResponse(
                operation=connector_sdk_pb2.Operation(record=record)))

        return responses

    @staticmethod
    def update(table: str, modified: dict) -> connector_sdk_pb2.UpdateResponse:
        """Performs an update operation on the specified table with the given modified data.

        Args:
            table (str): The name of the table.
            modified (dict): The modified data.

        Returns:
            connector_sdk_pb2.UpdateResponse: The update response.
        """
        if constants.DEBUGGING:
            _yield_check(inspect.stack())

        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(modified, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.UPDATE,
            data=mapped_data
        )

        return connector_sdk_pb2.UpdateResponse(
            operation=connector_sdk_pb2.Operation(record=record))

    @staticmethod
    def delete(table: str, keys: dict) -> connector_sdk_pb2.UpdateResponse:
        """Performs a soft delete operation on the specified table with the given keys.

        Args:
            table (str): The name of the table.
            keys (dict): The keys to delete.

        Returns:
            connector_sdk_pb2.UpdateResponse: The delete response.
        """
        if constants.DEBUGGING:
            _yield_check(inspect.stack())

        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(keys, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.DELETE,
            data=mapped_data
        )

        return connector_sdk_pb2.UpdateResponse(
            operation=connector_sdk_pb2.Operation(record=record))

    @staticmethod
    def checkpoint(state: dict) -> connector_sdk_pb2.UpdateResponse:
        """Checkpoint saves the connector's state. State is a dict which stores information to continue the
        sync from where it left off in the previous sync. For example, you may choose to have a field called
        "cursor" with a timestamp value to indicate up to when the data has been synced. This makes it possible
        for the next sync to fetch data incrementally from that time forward. See below for a few example fields
        which act as parameters for use by the connector code.\n
        {
            "initialSync": true,\n
            "cursor": "1970-01-01T00:00:00.00Z",\n
            "last_resync": "1970-01-01T00:00:00.00Z",\n
            "thread_count": 5,\n
            "api_quota_left": 5000000
        }

        Args:
            state (dict): The state to checkpoint/save.

        Returns:
            connector_sdk_pb2.UpdateResponse: The checkpoint response.
        """
        if constants.DEBUGGING:
            _yield_check(inspect.stack())

        return connector_sdk_pb2.UpdateResponse(
            operation=connector_sdk_pb2.Operation(checkpoint=connector_sdk_pb2.Checkpoint(
                state_json=json.dumps(state))))

def _get_columns(table: str) -> dict:
    """Retrieves the columns for the specified table.

    Args:
        table (str): The name of the table.

    Returns:
        dict: The columns for the table.
    """
    columns = {}
    if table in TABLES:
        for column in TABLES[table].columns:
            columns[column.name] = column

    return columns


def _map_data_to_columns(data: dict, columns: dict) -> dict:
    """Maps data to the specified columns.

    Args:
        data (dict): The data to map.
        columns (dict): The columns to map the data to.

    Returns:
        dict: The mapped data.
    """
    mapped_data = {}
    for k, v in data.items():
        key = get_renamed_column_name(k)
        if v is None:
            mapped_data[key] = common_pb2.ValueType(null=True)
        elif (key in columns) and columns[key].type != common_pb2.DataType.UNSPECIFIED:
            map_defined_data_type(columns, key, mapped_data, v)
        else:
            map_inferred_data_type(key, mapped_data, v)
    return mapped_data

def map_inferred_data_type(k, mapped_data, v):
    # We can infer type from the value
    if isinstance(v, int):
        if abs(v) > JAVA_LONG_MAX_VALUE:
            mapped_data[k] = common_pb2.ValueType(float=v)
        else:
            mapped_data[k] = common_pb2.ValueType(long=v)
    elif isinstance(v, float):
        mapped_data[k] = common_pb2.ValueType(float=v)
    elif isinstance(v, bool):
        mapped_data[k] = common_pb2.ValueType(bool=v)
    elif isinstance(v, bytes):
        mapped_data[k] = common_pb2.ValueType(binary=v)
    elif isinstance(v, list):
        raise ValueError(
            "Values for the columns cannot be of type 'list'. Please ensure that all values are of a supported type. Reference: https://fivetran.com/docs/connectors/connector-sdk/technical-reference#supporteddatatypes")
    elif isinstance(v, dict):
        mapped_data[k] = common_pb2.ValueType(json=json.dumps(v))
    elif isinstance(v, str):
        mapped_data[k] = common_pb2.ValueType(string=v)
    else:
        # Convert arbitrary objects to string
        mapped_data[k] = common_pb2.ValueType(string=str(v))


def map_defined_data_type(columns, k, mapped_data, v):
    if columns[k].type == common_pb2.DataType.BOOLEAN:
        mapped_data[k] = common_pb2.ValueType(bool=v)
    elif columns[k].type == common_pb2.DataType.SHORT:
        mapped_data[k] = common_pb2.ValueType(short=v)
    elif columns[k].type == common_pb2.DataType.INT:
        mapped_data[k] = common_pb2.ValueType(int=v)
    elif columns[k].type == common_pb2.DataType.LONG:
        mapped_data[k] = common_pb2.ValueType(long=v)
    elif columns[k].type == common_pb2.DataType.DECIMAL:
        mapped_data[k] = common_pb2.ValueType(decimal=v)
    elif columns[k].type == common_pb2.DataType.FLOAT:
        mapped_data[k] = common_pb2.ValueType(float=v)
    elif columns[k].type == common_pb2.DataType.DOUBLE:
        mapped_data[k] = common_pb2.ValueType(double=v)
    elif columns[k].type == common_pb2.DataType.NAIVE_DATE:
        timestamp = timestamp_pb2.Timestamp()
        dt = datetime.strptime(v, "%Y-%m-%d")
        timestamp.FromDatetime(dt)
        mapped_data[k] = common_pb2.ValueType(naive_date=timestamp)
    elif columns[k].type == common_pb2.DataType.NAIVE_DATETIME:
        if '.' not in v: v = v + ".0"
        timestamp = timestamp_pb2.Timestamp()
        dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
        timestamp.FromDatetime(dt)
        mapped_data[k] = common_pb2.ValueType(naive_datetime=timestamp)
    elif columns[k].type == common_pb2.DataType.UTC_DATETIME:
        timestamp = timestamp_pb2.Timestamp()
        dt = v if isinstance(v, datetime) else _parse_datetime_str(v)
        timestamp.FromDatetime(dt)
        mapped_data[k] = common_pb2.ValueType(utc_datetime=timestamp)
    elif columns[k].type == common_pb2.DataType.BINARY:
        mapped_data[k] = common_pb2.ValueType(binary=v)
    elif columns[k].type == common_pb2.DataType.XML:
        mapped_data[k] = common_pb2.ValueType(xml=v)
    elif columns[k].type == common_pb2.DataType.STRING:
        incoming = v if isinstance(v, str) else str(v)
        mapped_data[k] = common_pb2.ValueType(string=incoming)
    elif columns[k].type == common_pb2.DataType.JSON:
        mapped_data[k] = common_pb2.ValueType(json=json.dumps(v))
    else:
        raise ValueError(f"Unsupported data type encountered: {columns[k].type}. Please use valid data types.")

def _parse_datetime_str(dt):
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z" if '.' in dt else "%Y-%m-%dT%H:%M:%S%z")


def _yield_check(stack):
    """Checks for the presence of 'yield' in the calling code.
    Args:
        stack: The stack frame to check.
    """

    # Known issue with inspect.getmodule() and yield behavior in a frozen application.
    # When using inspect.getmodule() on stack frames obtained by inspect.stack(), it fails
    # to resolve the modules in a frozen application due to incompatible assumptions about
    # the file paths. This can lead to unexpected behavior, such as yield returning None or
    # the failure to retrieve the module inside a frozen app
    # (Reference: https://github.com/pyinstaller/pyinstaller/issues/5963)

    called_method = stack[0].function
    calling_code = stack[1].code_context[0]
    if f"{called_method}(" in calling_code:
        if 'yield' not in calling_code:
            print_library_log(
                f"Please add 'yield' to '{called_method}' operation on line {stack[1].lineno} in file '{stack[1].filename}'", Logging.Level.SEVERE)
            os._exit(1)
    else:
        # This should never happen
        raise RuntimeError(
            f"The '{called_method}' function is missing in the connector calling code '{calling_code}'. Please ensure that the '{called_method}' function is properly defined in your code to proceed. Reference: https://fivetran.com/docs/connectors/connector-sdk/technical-reference#technicaldetailsmethods")

