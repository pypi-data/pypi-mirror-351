import warnings
from datetime import datetime

import typer
from rich.console import Console
from typing_extensions import Annotated

from cruxctl.command_groups.dataset_health.big_query_dataset_health_repo import (
    BiqQueryDatasetHealthRepo,
)
from cruxctl.command_groups.dataset_health.health_tree_data_adapter import (
    HealthTreeDataAdapter,
)
from cruxctl.command_groups.dataset_health.postgres_dataset_health_repo import (
    PostgresDatasetHealthRepo,
)
from cruxctl.command_groups.profile.profile import get_current_profile
from cruxctl.common.callbacks import datetime_to_date
from cruxctl.common.utils.data_adapter_utils import get_data_adapter
from cruxctl.common.utils.api_utils import set_api_token
from cruxctl.common.utils.env_utils import get_mixpanel_token
from cruxctl.common.utils.mixpanel_utils import track_mixpanel_event
from cruxctl.common.models.data_format import DataFormat
from cruxctl.common.typer_constants import (
    PROFILE_OPTION,
    LISTING_LIMIT_OPTION,
    PROFILE_OPTION_TEST_ONLY,
    DATABASE_USER_OPTION,
    DATABASE_PASSWORD_OPTION,
    DATABASE_HOST_OPTION,
)

app = typer.Typer()

console = Console()

warnings.filterwarnings("ignore")


@app.command("get-all-processing-health")
def get_all_processing_health(
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Lists all dataset processing health entries
    """
    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-all-processing-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    result = BiqQueryDatasetHealthRepo().get_all_processing_health(
        profile, data_adapter, delivery_deadline_date=delivery_deadline, limit=limit
    )

    console.print(result)


@app.command("get-processing-health")
def get_processing_health(
    dataset_id: Annotated[
        str, typer.Option("--dataset-id", "-d", help="Dataset ID to get for")
    ],
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Gets the dataset processing health entries matching the dataset ID
    """
    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-processing-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    result = BiqQueryDatasetHealthRepo().get_processing_health_by_dataset_id(
        profile,
        data_adapter,
        dataset_id=dataset_id,
        delivery_deadline_date=delivery_deadline,
    )

    console.print(result)


@app.command("get-all-dispatch-health")
def get_all_dispatch_health(
    limit: Annotated[int, LISTING_LIMIT_OPTION] = 100,
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Lists all dataset dispatch health entries
    """
    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-all-dispatch-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    result = BiqQueryDatasetHealthRepo().get_all_dispatch_health(
        profile, data_adapter, delivery_deadline_date=delivery_deadline, limit=limit
    )

    console.print(result)


@app.command("get-dispatch-health")
def get_dispatch_health(
    dataset_id: Annotated[
        str, typer.Option("--dataset-id", "-d", help="Dataset ID to get for")
    ],
    subscriber_id: Annotated[
        str, typer.Option("--subscriber-id", "-s", help="Subscriber ID to get for")
    ] = None,
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Gets the dataset processing health entries matching either the dataset_id
    and/or the subscriber ID. At least one of
    the IDs must be provided.
    """
    if not dataset_id and not subscriber_id:
        raise typer.BadParameter("Either dataset_id or subscriber_id must be provided")

    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-dispatch-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    result = BiqQueryDatasetHealthRepo().get_dispatch_health(
        profile,
        data_adapter,
        dataset_id=dataset_id,
        subscriber_id=subscriber_id,
        delivery_deadline_date=delivery_deadline,
    )

    console.print(result)


@app.command("get-dataset-health-grouped-by-dataset")
def get_dataset_health_grouped_by_dataset(
    dataset_id: Annotated[
        str, typer.Option("--dataset-id", "-d", help="Dataset ID to get for")
    ] = None,
    subscriber_id: Annotated[
        str, typer.Option("--subscriber-id", "-s", help="Subscriber ID to get for")
    ] = None,
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Gets the overall dataset health entries grouped by the dataset ID
    """
    data_adapter = (
        HealthTreeDataAdapter().bigquery_to_health_tree_by_dataset
        if output_format == DataFormat.tree
        else get_data_adapter(output_format)
    )
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-dataset-health-grouped-by-dataset"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    result = BiqQueryDatasetHealthRepo().get_dataset_health_grouped_by_dataset(
        profile,
        data_adapter,
        dataset_id=dataset_id,
        subscriber_id=subscriber_id,
        delivery_deadline_date=delivery_deadline,
    )

    console.print(result)


@app.command("get-dataset-health-grouped-by-subscriber")
def get_dataset_health_grouped_by_subscriber(
    dataset_id: Annotated[
        str, typer.Option("--dataset-id", "-d", help="Dataset ID to get for")
    ] = None,
    subscriber_id: Annotated[
        str, typer.Option("--subscriber-id", "-s", help="Subscriber ID to get for")
    ] = None,
    delivery_deadline: Annotated[
        datetime,
        typer.Option(
            "--delivery-deadline",
            "-dd",
            formats=["%Y-%m-%d"],
            help="Filters on delivery deadlines that fall on this date",
            callback=datetime_to_date,
        ),
    ] = None,
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
    Gets the overall dataset health entries grouped by the subscriber ID
    """
    data_adapter = (
        HealthTreeDataAdapter().bigquery_to_health_tree_by_subscriber
        if output_format == DataFormat.tree
        else get_data_adapter(output_format)
    )
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-dataset-health-grouped-by-subscriber"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    result = BiqQueryDatasetHealthRepo().get_dataset_health_grouped_by_subscriber(
        profile,
        data_adapter,
        dataset_id=dataset_id,
        subscriber_id=subscriber_id,
        delivery_deadline_date=delivery_deadline,
    )

    console.print(result)


@app.command("get-all-notification-history")
def get_all_notification_history(
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            min=-1,
            help="Limit for the number of entries to return. Use -1 for unlimited",
        ),
    ] = 100,
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
    Lists all the notification history entries
    """
    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-all-notification-history"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    console.print(
        BiqQueryDatasetHealthRepo().get_all_notification_history(
            profile, data_adapter, limit=limit
        )
    )


@app.command("get-notification-history")
def get_notification_history(
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
    Gets the notification history entries matching the dataset ID
    """
    data_adapter = get_data_adapter(output_format)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "get-notification-history"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )
    console.print(
        BiqQueryDatasetHealthRepo().get_notification_history_by_dataset_id(
            profile, data_adapter, dataset_id
        )
    )


@app.command("delete-all-processing-health")
def delete_all_processing_health(
    _: Annotated[str, PROFILE_OPTION_TEST_ONLY],
    user: Annotated[str, DATABASE_USER_OPTION],
    password: Annotated[str, DATABASE_PASSWORD_OPTION],
    host: Annotated[str, DATABASE_HOST_OPTION],
):
    """
    Deletes all processing health. Allowed only for test profile. Use with caution.
    """
    (
        PostgresDatasetHealthRepo(
            user=user, password=password, host=host, database="crux", port=5432
        ).delete_all_processing_health()
    )
    profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "delete-all-processing-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    console.print("[green]All processing health entries deleted successfully[/green]")


@app.command("delete-all-dispatch-health")
def delete_all_dispatch_health(
    _: Annotated[str, PROFILE_OPTION_TEST_ONLY],
    user: Annotated[str, DATABASE_USER_OPTION],
    password: Annotated[str, DATABASE_PASSWORD_OPTION],
    host: Annotated[str, DATABASE_HOST_OPTION],
):
    """
    Deletes all dispatch health. Allowed only for test profile. Use with caution.
    """
    (
        PostgresDatasetHealthRepo(
            user=user, password=password, host=host, database="crux", port=5432
        ).delete_all_dispatch_health()
    )
    profile = get_current_profile()
    token = set_api_token(console, profile)
    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset-health",
        {"Command Name": "delete-all-processing-health"},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    console.print("[green]All dispatch health entries deleted successfully[/green]")
