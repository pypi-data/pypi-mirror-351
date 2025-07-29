from datetime import datetime

import typer
from rich.console import Console
from typing_extensions import Annotated

from cruxctl.command_groups.deadlines.dataset_snooze_client import DatasetSnoozeClient
from cruxctl.command_groups.deadlines.deadline_validations import (
    is_snooze_duration_excessive,
)
from cruxctl.command_groups.deadlines.models.deadline_notification_snooze_units import (
    DeadlineNotificationSnoozeUnits,
)
from cruxctl.common.models.data_format import DataFormat
from cruxctl.common.typer_constants import (
    PROFILE_OPTION,
    LISTING_LIMIT_OPTION,
    SORT_BY_OPTION,
    FILTERS_OPTION,
    PAGINATION_TOKEN_OPTION,
    DATA_FORMAT_OPTION,
)
from cruxctl.common.utils.api_utils import set_api_token

app = typer.Typer()
console = Console()


@app.command("get-all-notification-snooze")
def get_all_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
    limit: Annotated[int, LISTING_LIMIT_OPTION] = 100,
    sort_by: Annotated[str, SORT_BY_OPTION] = None,
    filters: Annotated[str, FILTERS_OPTION] = None,
    pagination_token: Annotated[str, PAGINATION_TOKEN_OPTION] = None,
    output_format: Annotated[DataFormat, DATA_FORMAT_OPTION] = DataFormat.table,
):
    """
    Lists all delivery deadline notification snooze entries
    """
    token: str = set_api_token(console, profile)

    console.print(
        DatasetSnoozeClient().get_all_notification_snooze(
            profile=profile,
            api_token=token,
            sort_by=sort_by,
            limit=limit,
            filters=filters,
            pagination_token=pagination_token,
            output_format=output_format,
        )
    )


@app.command("get-notification-snooze")
def get_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
    dataset_id: Annotated[str, typer.Argument(help="Dataset ID to get for")],
    output_format: Annotated[DataFormat, DATA_FORMAT_OPTION] = DataFormat.table,
):
    """
    Gets the delivery deadline notification snooze entries matching the dataset ID
    """
    token: str = set_api_token(console, profile)

    console.print(
        DatasetSnoozeClient().get_notification_snooze_by_dataset_id(
            profile=profile,
            api_token=token,
            output_format=output_format,
            dataset_id=dataset_id,
        )
    )


@app.command("create-notification-snooze")
def create_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
    dataset_id: Annotated[
        str, typer.Argument(help="Dataset ID to snooze notifications for")
    ],
    snooze_duration: Annotated[
        int, typer.Argument(help="Defines how long to snooze for", min=1)
    ],
    snooze_units: Annotated[
        DeadlineNotificationSnoozeUnits,
        typer.Argument(help="Units for the snooze duration.", case_sensitive=False),
    ],
    snooze_start_time: Annotated[
        datetime,
        typer.Argument(
            formats=["%Y-%m-%dT%H:%M:%S"],
            help="The datetime (in UTC) at which the snooze will start on.\n"
            "If not defined, will start immediately.",
        ),
    ] = None,
):
    """
    Creates a notification snooze for the delivery deadline entries with the given dataset ID.
    """
    if is_snooze_duration_excessive(snooze_duration, snooze_units):
        is_proceed = typer.confirm(
            "The snooze duration is more than 2 weeks. Do you want to proceed?",
            default=False,
        )
        if not is_proceed:
            return

    token: str = set_api_token(console, profile)

    existing_snooze_table = DatasetSnoozeClient().get_notification_snooze_by_dataset_id(
        profile=profile,
        api_token=token,
        output_format=DataFormat.table,
        dataset_id=dataset_id,
    )

    if existing_snooze_table.row_count > 0:
        console.print(existing_snooze_table)

        is_proceed = typer.confirm(
            f"There are existing notification snoozes with dataset ID: {dataset_id}. "
            f"Creating a new one will delete the existing ones. Do you want to proceed?",
            default=False,
        )
        if not is_proceed:
            return

        DatasetSnoozeClient().delete_notification_snooze_by_dataset_id(
            profile=profile, api_token=token, dataset_id=dataset_id
        )
        console.print(
            f"[green]Deleted notification snooze with dataset ID: {dataset_id}[/green]"
        )

    DatasetSnoozeClient().insert_notification_snooze(
        profile=profile,
        api_token=token,
        dataset_id=dataset_id,
        snooze_duration=snooze_duration,
        snooze_units=snooze_units,
        snooze_start_time=snooze_start_time,
    )

    console.print("[green]Notification snooze created successfully[/green]")


@app.command("delete-notification-snooze")
def delete_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
    dataset_id: Annotated[
        str, typer.Argument(help="Dataset ID to match for deleting notification snooze")
    ],
):
    """
    Deletes the delivery deadline notification snooze entry with the given dataset ID
    """
    token: str = set_api_token(console, profile)
    DatasetSnoozeClient().delete_notification_snooze_by_dataset_id(
        profile=profile, api_token=token, dataset_id=dataset_id
    )
    console.print(
        f"[green]Deleted notification snooze with dataset ID: {dataset_id}[/green]"
    )


@app.command("delete-expired-notification-snooze")
def delete_expired_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
):
    """
    Deletes all expired delivery deadline notification snooze entries
    """
    token: str = set_api_token(console, profile)
    DatasetSnoozeClient().delete_expired_notification_snoozes(
        profile=profile, api_token=token
    )
    console.print(
        "[green]Deleted all expired notification snoozes successfully[/green]"
    )


@app.command("update-notification-snooze")
def update_notification_snooze(
    profile: Annotated[str, PROFILE_OPTION],
    dataset_id: Annotated[
        str, typer.Argument(help="Dataset ID to match for deleting notification snooze")
    ],
    snooze_id: Annotated[
        str, typer.Argument(help="Snooze ID to match for deleting notification snooze")
    ],
    snooze_duration: Annotated[
        int, typer.Argument(help="Defines how long to snooze for", min=1)
    ],
    snooze_units: Annotated[
        DeadlineNotificationSnoozeUnits,
        typer.Argument(help="Units for the snooze duration.", case_sensitive=False),
    ],
    snooze_start_time: Annotated[
        datetime,
        typer.Argument(
            formats=["%Y-%m-%dT%H:%M:%S"],
            help="The datetime (in UTC) at which the snooze will start on. "
            "If not defined, will start immediately.",
        ),
    ] = None,
):
    """
    Deletes all expired delivery deadline notification snooze entries
    """
    token: str = set_api_token(console, profile)
    DatasetSnoozeClient().update_notification_snooze(
        profile=profile,
        dataset_id=dataset_id,
        api_token=token,
        snooze_id=snooze_id,
        snooze_duration=snooze_duration,
        snooze_units=snooze_units,
        snooze_start_time=snooze_start_time,
    )
    console.print("[green]Updated notification snooze successfully[/green]")


if __name__ == "__main__":
    app()
