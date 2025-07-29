from typing import Callable

from cruxctl.common.data_adapters import bigquery_to_richtable, bigquery_to_json
from cruxctl.common.models.data_format import DataFormat


def get_data_adapter(data_format: DataFormat) -> Callable:
    if data_format == DataFormat.table:
        return bigquery_to_richtable

    if data_format == DataFormat.json:
        return bigquery_to_json

    raise ValueError(f"Unsupported data format: {data_format}")
