import typer
import itertools
from enum import Enum
from typing import Dict, Any, List
from rich.console import Console
from crux_odin.dataclass import AvailabilityDeadline
from crux_odin.types.deadlines import (
    DeadlineMinute,
    DeadlineHour,
    DeadlineDayOfMonth,
    DeadlineMonth,
    DeadlineDayOfWeek,
    DeadlineYear,
    FileFrequency,
    Timezone,
)


class OperationMode(str, Enum):
    """
    The operation mode for command execution.
    """

    append = "append"
    replace = "replace"


def process_recommended_deadline(recommended_deadline: Dict[str, Any]) -> str:
    last_available_end = recommended_deadline.get("latest_time_processing_end")
    cron_end = recommended_deadline.get("schedule_processing_end")
    if last_available_end is not None:
        deadline_cron_end = set_cron_time(cron_end, last_available_end) + " *"
    else:
        deadline_cron_end = cron_end + " *"
    return deadline_cron_end


def normalize_frequencies(cadence: str) -> str:
    cadence_to_file_frequency = {
        "annually": "yearly",
        "quarterly": "semi-annual",
        "monthly": "monthly",
        "weekly": "weekly",
        "daily": "daily",
        "hourly": "intraday",
        "minute_30": "intraday",
        "minute_15": "intraday",
    }
    return cadence_to_file_frequency.get(cadence)


def set_cron_time(cron: str, time_string: str) -> str:
    cron_parts = cron.split(" ")

    time_parts = time_string.split(":")

    cron_parts[0] = str(int(time_parts[1]))
    cron_parts[1] = str(int(time_parts[0]))

    new_cron = " ".join(cron_parts)

    return new_cron


def partition_cron(cron: str) -> list:
    """
    Splits a cron string into all possible combinations for each field.

    For example, a cron string like "1,2 * * * *" will be split into
    ["1 * * * *", "2 * * * *"].

    This function will perform this operation for each field in the cron string.

    Args:
        cron (str): The cron string to split.

    Returns:
        List[str]: A list of cron strings with all combinations of fields.
    """
    cron_parts = cron.split(" ")
    cron_fields = [part.split(",") if "," in part else [part] for part in cron_parts]
    cron_combinations = list(itertools.product(*cron_fields))
    return [" ".join(combination) for combination in cron_combinations]


def delete_existing_deadline_prompt(
    console: Console, existing_deadlines: List[AvailabilityDeadline]
) -> bool:
    console.print("Existing Deadline(s):")
    console.print(existing_deadlines)
    is_delete = typer.confirm(
        "There are existing entries for this datasetID. Do you want to delete them "
        "before inserting?",
        default=True,
    )
    return is_delete


def create_custom_deadline(
    deadline_minute: DeadlineMinute = None,
    deadline_hour: DeadlineHour = None,
    deadline_day_of_month: DeadlineDayOfMonth = None,
    deadline_month: DeadlineMonth = None,
    deadline_day_of_week: DeadlineDayOfWeek = None,
    deadline_year: DeadlineYear = None,
    file_frequency: FileFrequency = None,
    timezone: Timezone = None,
) -> AvailabilityDeadline:
    if deadline_minute is None:
        deadline_minute = DeadlineMinute(typer.prompt("Enter deadline minute"))

    if deadline_hour is None:
        deadline_hour = DeadlineHour(typer.prompt("Enter deadline hour"))

    if deadline_day_of_month is None:
        deadline_day_of_month = DeadlineDayOfMonth(
            typer.prompt("Enter deadline day of the month")
        )

    if deadline_month is None:
        deadline_month = DeadlineMonth(typer.prompt("Enter deadline month"))

    if deadline_day_of_week is None:
        deadline_day_of_week = DeadlineDayOfWeek(
            typer.prompt("Enter deadline day of the week")
        )

    if deadline_year is None:
        deadline_year = DeadlineYear(typer.prompt("Enter deadline year"))

    if file_frequency is None:
        file_frequency = FileFrequency(typer.prompt("Enter file frequency"))

    if timezone is None:
        timezone = Timezone(typer.prompt("Enter timezone"))

    custom_deadline = AvailabilityDeadline(
        deadline_minute=deadline_minute,
        deadline_hour=deadline_hour,
        deadline_day_of_month=deadline_day_of_month,
        deadline_month=deadline_month,
        deadline_day_of_week=deadline_day_of_week,
        deadline_year=deadline_year,
        file_frequency=file_frequency,
        timezone=timezone,
    )

    return custom_deadline


def apply_recommended_deadline_prompt(
    console: Console, recommended_deadlines: List[AvailabilityDeadline]
) -> bool:
    console.print("Recommended Deadline(s):")
    console.print(recommended_deadlines)
    is_apply = typer.confirm(
        "There are recommended deadlines for this datasetID. Do you want to apply them?",
        default=True,
    )
    return is_apply
