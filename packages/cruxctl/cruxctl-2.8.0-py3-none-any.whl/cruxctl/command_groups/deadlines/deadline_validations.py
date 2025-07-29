import csv
from pathlib import Path
from typing import Callable, Optional

import typer
from google.cloud.bigquery.table import RowIterator

from cruxctl.command_groups.deadlines.dataset_deadline_client import (
    DatasetDeadlineClient,
)
from cruxctl.command_groups.deadlines.models.dataset_expected_delivery_deadline_columns import (
    DatasetExpectedDeliveryDeadlineJoinedColumn,
    DatasetExpectedDeliveryDeadlineColumnCamelCase,
)
from cruxctl.command_groups.deadlines.models.deadline_notification_snooze_units import (
    DeadlineNotificationSnoozeUnits,
)
from cruxctl.command_groups.deadlines.models.deadline_row import DeadlineRow
from cruxctl.common.models.data_format import DataFormat
from cruxctl.common.valid_timezones import VALID_TIMEZONES

EXCESSIVE_SNOOZE_THRESHOLD_DAYS = 14


def default_cron_validation(
    ctx: typer.Context,
    cron_element: str,
    lower_bound: int,
    upper_bound: int,
    cron_element_label: str,
    *args,
    asterisk_allowed: bool = True,
    extra_validation: Callable = None,
):
    if ctx.resilient_parsing:
        return

    if asterisk_allowed and cron_element == "*":
        return cron_element

    if extra_validation and extra_validation(cron_element, *args):
        return cron_element

    try:
        cron_element_int = int(cron_element)

        if cron_element_int < lower_bound or cron_element_int > upper_bound:
            raise typer.BadParameter(
                f"{cron_element_label} must be between {lower_bound}-{upper_bound}"
            )
    except ValueError:
        raise typer.BadParameter(f"{cron_element_label} is not a valid value")

    return cron_element


def deadline_minute_validation(ctx: typer.Context, deadline_minute: str):
    return default_cron_validation(
        ctx, deadline_minute, 0, 59, "Deadline minute", asterisk_allowed=False
    )


def deadline_hour_validation(ctx: typer.Context, deadline_hour: str):
    return default_cron_validation(ctx, deadline_hour, 0, 23, "Deadline hour")


def _validate_weekday_expression(deadline_day_of_the_month: str) -> bool:
    if deadline_day_of_the_month == "*W":
        return True

    if deadline_day_of_the_month.endswith("W"):
        try:
            day_of_month_value = int(deadline_day_of_the_month[:-1])

            if day_of_month_value < 1 or day_of_month_value > 31:
                raise typer.BadParameter("Deadline day of month must be between 1-31")

            return True
        except ValueError:
            raise typer.BadParameter("Deadline day of month is not a valid value")

    return False


def _validate_cron_interval(
    expression: str, lower_bound: int, upper_bound: int
) -> bool:
    if "-" in expression:
        try:
            split_expression = expression.split("-")

            if len(split_expression) != 2:
                raise typer.BadParameter(
                    f"Invalid cron interval expression: {expression}"
                )

            lower_input = int(split_expression[0])
            upper_input = int(split_expression[1])

            if (
                lower_input < lower_bound
                or upper_input > upper_bound
                or lower_input >= upper_input
            ):
                raise typer.BadParameter(
                    f"Expression {expression} must be a valid bound between "
                    f"{lower_bound}-{upper_bound}"
                )

            return True
        except ValueError:
            raise typer.BadParameter(f"Invalid cron interval expression: {expression}")

    return False


def deadline_day_of_the_month_validation(
    ctx: typer.Context, deadline_day_of_the_month: str
):
    return default_cron_validation(
        ctx,
        deadline_day_of_the_month,
        1,
        31,
        "Deadline day of month",
        extra_validation=_validate_weekday_expression,
    )


def deadline_month_validation(ctx: typer.Context, deadline_month: str):
    return default_cron_validation(ctx, deadline_month, 1, 12, "Deadline month")


def deadline_day_of_week_validation(ctx: typer.Context, deadline_day_of_week: str):
    return default_cron_validation(
        ctx,
        deadline_day_of_week,
        0,
        6,
        "Deadline day of week",
        0,
        6,
        extra_validation=_validate_cron_interval,
    )


def deadline_year_validation(ctx: typer.Context, deadline_year):
    if ctx.resilient_parsing:
        return

    if deadline_year != "*":
        raise typer.BadParameter("Currently the deadline year must be *")

    return deadline_year


def timezone_validation(ctx: typer.Context, timezone: Optional[str] = None):
    if ctx.resilient_parsing:
        return

    if timezone and timezone not in VALID_TIMEZONES:
        raise typer.BadParameter(f"Invalid timezone: {timezone}")

    return timezone


def _validate_csv_header(reader: csv.DictReader):
    header = set(reader.fieldnames)
    expected_header = {c.value for c in DatasetExpectedDeliveryDeadlineColumnCamelCase}

    if header != expected_header:
        raise typer.BadParameter(
            f"Invalid CSV header. CSV header must match the following:\n{expected_header}"
        )


def bigquery_to_deadline_row_set(bq_row_iterator: RowIterator) -> set[tuple]:
    results = set()

    for bq_row in bq_row_iterator:
        entry = (
            *(
                str(bq_row.get(column) or "")
                for column in bq_row.keys()
                if column
                != DatasetExpectedDeliveryDeadlineJoinedColumn.workflow_id.value
            ),
        )
        results.add(entry)

    return results


def _validate_row_formatting(ctx: typer.Context, row: DeadlineRow):
    deadline_minute_validation(ctx, row.deadline_minute)
    deadline_hour_validation(ctx, row.deadline_hour)
    deadline_day_of_the_month_validation(ctx, row.deadline_day_of_the_month)
    deadline_month_validation(ctx, row.deadline_month)
    deadline_day_of_week_validation(ctx, row.deadline_day_of_week)
    deadline_year_validation(ctx, row.deadline_year)
    timezone_validation(ctx, row.timezone)


def _validate_duplicate_row(row: DeadlineRow, duplicate_set: set, source_label: str):
    row_key = row.to_key()

    if row_key in duplicate_set:
        raise typer.BadParameter(
            f"Duplicate row found within the {source_label}: {row_key}"
        )

    duplicate_set.add(row_key)


def _validate_duplicate_dataset_ids(
    row: DeadlineRow, dataset_ids: set, source_label: str
):
    if row.dataset_id in dataset_ids:
        raise typer.BadParameter(
            f"Duplicate dataset ID found within the {source_label}: {row.dataset_id}"
        )


def csv_file_validation(
    ctx: typer.Context,
    profile: str,
    csv_file_path: Path,
    token: str = None,
):
    if ctx.resilient_parsing:
        return

    with open(csv_file_path) as csv_file:
        reader = csv.DictReader(csv_file)

        _validate_csv_header(reader)

        duplicate_database_list = DatasetDeadlineClient().get_all_deadlines(
            profile=profile, token=token, output_format=DataFormat.json
        )
        unique_dataset_ids = {item["datasetId"] for item in duplicate_database_list}
        duplicate_file_set = set()

        for row in reader:
            ddotm = (
                DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_day_of_the_month
            )
            try:
                deadline_row = DeadlineRow(
                    dataset_id=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.dataset_id.value
                    ],
                    deadline_minute=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_minute.value
                    ],
                    deadline_hour=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_hour.value
                    ],
                    deadline_day_of_the_month=row[(ddotm.value)],
                    deadline_month=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_month.value
                    ],
                    deadline_day_of_week=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_day_of_week.value
                    ],
                    deadline_year=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.deadline_year.value
                    ],
                    timezone=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.timezone.value
                    ],
                    file_frequency=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.file_frequency.value
                    ],
                    is_active=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.is_active.value
                    ],
                    is_excluded=row[
                        DatasetExpectedDeliveryDeadlineColumnCamelCase.is_excluded.value
                    ],
                )

                _validate_row_formatting(ctx, deadline_row)
                _validate_duplicate_row(deadline_row, duplicate_file_set, "CSV file")
                _validate_duplicate_dataset_ids(
                    deadline_row, unique_dataset_ids, "database"
                )
            except typer.BadParameter as e:
                message = f"CSV file validation failed at line {reader.line_num}.\n{e.message}"
                raise typer.BadParameter(message=message, ctx=ctx)


def is_snooze_duration_excessive(
    snooze_duration: int, snooze_units: DeadlineNotificationSnoozeUnits
):
    return (
        snooze_duration > EXCESSIVE_SNOOZE_THRESHOLD_DAYS
        if snooze_units == DeadlineNotificationSnoozeUnits.days
        else snooze_duration > EXCESSIVE_SNOOZE_THRESHOLD_DAYS * 24
    )
