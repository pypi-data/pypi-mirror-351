import json

from google.cloud.bigquery.table import RowIterator
from rich.table import Table, Column


def bigquery_to_richtable(bq_row_iterator: RowIterator) -> Table:
    table = Table(
        *[Column(field.name, overflow="fold") for field in bq_row_iterator.schema]
    )

    for bq_row in bq_row_iterator:
        table.add_row(*[str(bq_row.get(column)) for column in bq_row.keys()])

    return table


def bigquery_to_json(bq_row_iterator: RowIterator) -> str:
    results = []

    for bq_row in bq_row_iterator:
        entry = {column: str(bq_row.get(column)) for column in bq_row.keys()}
        results.append(entry)

    return json.dumps(results)


def json_to_rich_table(json_data: list) -> Table:
    table: Table
    if len(json_data) == 0:
        table = Table()
    else:
        table = Table(*[Column(key, overflow="fold") for key in json_data[0].keys()])
        for entry in json_data:
            table.add_row(*[str(entry[key]) for key in entry.keys()])
    return table
