from typing import Optional

import warnings
from pathlib import Path

import typer
from rich.console import Console
from typing_extensions import Annotated

from cruxctl.command_groups.deadlines import deadlines_snooze
from cruxctl.command_groups.deadlines.dataset_deadline_client import (
    DatasetDeadlineClient,
)
from cruxctl.command_groups.profile.profile import get_current_profile
from cruxctl.common.models.data_format import DataFormat
from cruxctl.command_groups.deadlines.deadline_validations import (
    csv_file_validation,
)
from cruxctl.common.models.file_frequency import FileFrequency

from cruxctl.common.typer_constants import PROFILE_OPTION, LISTING_LIMIT_OPTION
from cruxctl.common.utils.api_utils import set_api_token
from cruxctl.common.utils.env_utils import get_mixpanel_token
from cruxctl.common.utils.mixpanel_utils import track_mixpanel_event

app = typer.Typer()
app.registered_commands += deadlines_snooze.app.registered_commands

console = Console()

warnings.filterwarnings("ignore")


@app.command("get-all")
def get_all(
    limit: Annotated[int, LISTING_LIMIT_OPTION] = 100,
    output_format: Annotated[
        DataFormat,
        typer.Option(
            "--output-format",
            "-o",
            case_sensitive=False,
            help="The output display format",
        ),
    ] = DataFormat.table,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Lists all delivery deadline entries
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "get-all"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    console.print(
        DatasetDeadlineClient().get_all_deadlines(
            profile=profile, token=token, limit=limit, output_format=output_format
        )
    )


@app.command()
def get(
    dataset_id: Annotated[str, typer.Argument(help="Dataset ID to get for")],
    output_format: Annotated[
        DataFormat,
        typer.Option(
            "--output-format",
            "-o",
            case_sensitive=False,
            help="The output display format",
        ),
    ] = DataFormat.table,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Gets the delivery deadline entries matching the dataset ID
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "get", "Dataset ID": dataset_id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    console.print(
        DatasetDeadlineClient().get_all_deadlines(
            profile=profile,
            token=token,
            output_format=output_format,
            dataset_id=dataset_id,
        )
    )


@app.command()
def upsert(
    dataset_id: Annotated[
        str, typer.Argument(help="V1 Dataset ID of the deadline to insert")
    ],
    deadline_minute: Annotated[
        str,
        typer.Argument(
            help=(
                "Minute of the delivery deadline. Allowed values: 0-59. "
                "Leave 0 if unspecified."
            ),
        ),
    ],
    deadline_hour: Annotated[
        str,
        typer.Argument(
            help=("Hour of the delivery deadline. Allowed values: 0-23."),
        ),
    ],
    deadline_day_of_the_month: Annotated[
        str,
        typer.Argument(
            help=(
                "Day of the month delivery deadline. Allowed values: 1-31. "
                "Leave * if expected every day."
            ),
        ),
    ],
    deadline_month: Annotated[
        str,
        typer.Argument(
            help=(
                "Month of the delivery deadline. Allowed values: 1-12. "
                "Leave * if expected every month."
            ),
        ),
    ],
    deadline_day_of_week: Annotated[
        str,
        typer.Argument(
            help=(
                "Day of the week delivery deadline. Allowed values: 0-6. "
                "Leave * if expected every day."
            ),
        ),
    ],
    file_frequency: Annotated[
        FileFrequency,
        typer.Argument(
            help="Frequency of the file. Example values: daily, weekly, monthly, yearly"
        ),
    ],
    timezone: Annotated[
        Optional[str],
        typer.Argument(
            help=(
                "Timezone from which to calculate the delivery deadline. "
                "If unspecified it will use UTC. "
                "For the timezone format use the TZ identifier column found "
                "https://en.wikipedia.org/wiki/List_of_UTC_time_offsets."
            ),
        ),
    ] = "UTC",
    is_active: Annotated[
        bool,
        typer.Option(
            "--is-active",
            "-a",
            case_sensitive=False,
            help="Determines if the deadline is active",
        ),
    ] = True,
    is_excluded: Annotated[
        bool,
        typer.Option(
            "--is-excluded",
            "-e",
            case_sensitive=False,
            help="Determines if the deadline is excluded from Zendesk notifications",
        ),
    ] = False,
    delete_if_exists: Annotated[
        bool,
        typer.Option(
            "--delete-existing",
            "-d",
            case_sensitive=False,
            help="If set, deletes any existing deadlines for the dataset ID prior to upsert",
        ),
    ] = True,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Upserts a single delivery deadline
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "upsert", "Dataset ID": dataset_id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    DatasetDeadlineClient().upsert_deadline(
        profile,
        token,
        dataset_id,
        deadline_minute,
        deadline_hour,
        deadline_day_of_the_month,
        deadline_month,
        deadline_day_of_week,
        file_frequency,
        timezone,
        is_active,
        is_excluded,
        delete_if_exists,
    )

    console.print(f"[green]Upserted deadline for dataset {dataset_id}[/green]")


@app.command("import")
def bulk_import(
    ctx: typer.Context,
    file_path: Annotated[
        Path,
        typer.Argument(
            help="""
    Path to CSV file to import.\n
    The CSV must have a header with the following columns:\n
    dataset_id, deadline_minute, deadline_hour, deadline_day_of_month,
    deadline_month, deadline_day_of_week, deadline_year, timezone.\n
    [bold yellow]WARNING[/bold yellow]: No validation is performed on the CSV file.
    It is assumed that the content is valid and entries are deduplicated.
    """
        ),
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Imports a CSV file with the delivery deadline entries.
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "import", "File Path": str(file_path)},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    csv_file_validation(ctx, profile, file_path, token=token)

    DatasetDeadlineClient().bulk_insert_deadlines(
        profile, file_path=str(file_path), token=token
    )
    console.print("[green]Import completed successfully[/green]")


@app.command("export")
def bulk_export(
    file_path: Annotated[
        Path, typer.Argument(help="Path to CSV file to write data in locally")
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Exports a CSV file with all the delivery deadlines to the provided local path
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "export", "File Path": str(file_path)},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    DatasetDeadlineClient().export_to_local_file(
        profile, file_path=str(file_path), token=token
    )
    console.print("[green]Export completed successfully[/green]")


@app.command()
def delete(
    id: Annotated[str, typer.Argument(help="ID to match for deletion")],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Deletes the delivery deadline entries with the given ID
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "delete", "Deadline ID": id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    DatasetDeadlineClient().delete_deadline_by_id(profile, token, id)
    console.print(f"[green]Deleted entry with ID: {id}[/green]")


@app.command("dataset-delete")
def dataset_delete(
    dataset_id: Annotated[str, typer.Argument(help="dataset_id to match for deletion")],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Deletes the delivery deadline entries with the given dataset_id
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl deadlines",
        {"Command Name": "dataset-delete", "Dataset ID": dataset_id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    deadlines_by_dataset_id = DatasetDeadlineClient().get_all_deadlines(
        profile, token, dataset_id=dataset_id, output_format=DataFormat.json, limit=-1
    )

    console.print(deadlines_by_dataset_id)

    is_delete = typer.confirm(
        "Above are the entries matching with dataset_id, do you want to delete them?",
        default=False,
    )
    if is_delete:
        for deadline in deadlines_by_dataset_id:
            DatasetDeadlineClient().delete_deadline_by_id(
                profile, token, deadline["id"]
            )
        console.print(f"[green]Deleted entries with dataset ID: {dataset_id}[/green]")
    else:
        console.print("[red]No entries were deleted[/red]")
