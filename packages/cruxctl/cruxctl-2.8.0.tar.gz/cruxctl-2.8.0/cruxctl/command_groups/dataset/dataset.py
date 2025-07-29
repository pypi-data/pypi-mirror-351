import importlib
import json
import os.path
import re
import time
import warnings
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, List

import jsonschema
import pandas as pd
import requests
import typer
import yaml
from crux_odin.dataclass import (
    DeclaredField,
    DeclaredSchemaDef,
    Workflow,
    create_workflow,
)
from crux_odin.dict_utils import MergeDicts, yaml_file_to_dict
from crux_odin.validate_yaml import CustomValidations, validate_dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel
from rich.console import Console

import cruxctl
from cruxctl.command_groups.dataset.constants import CURATION_EVENT_TYPE, SchemaClass
from cruxctl.command_groups.dataset.dag_run_handler import DagRunHandler
from cruxctl.command_groups.dataset.dataset_utils import parse_cmd_line_yaml_lists
from cruxctl.command_groups.dataset.dispatch_run_handler import (
    DEFAULT_RERUN_QUEUE_KEY,
    DispatchRunHandler,
)
from cruxctl.command_groups.dataset.logs_handler import LogsHandler
from cruxctl.command_groups.dataset.models.export_activity_type import (
    ExportActivityType,
)
from cruxctl.command_groups.profile.profile import get_current_profile
from cruxctl.common.typer_constants import PROFILE_OPTION
from cruxctl.common.utils.api_utils import (
    get_control_plane_url,
    get_data_product_url,
    get_document_url,
    get_url_based_on_profile,
    get_user_info_by_token,
    set_api_token,
)
from cruxctl.common.utils.env_utils import get_mixpanel_token
from cruxctl.common.utils.mixpanel_utils import track_mixpanel_event

app = typer.Typer()
console = Console()
error_console = Console(stderr=True)
warnings.filterwarnings("ignore")


def format_events_line(event: dict[str, Any], full: bool) -> str:
    """
    Format an event line for printing.
    :param event: The event to format.
    :param full: Whether to print the full event or not.
    """
    assert event and isinstance(event, dict)
    assert "time" in event and isinstance(event["time"], str)
    assert "type" in event and isinstance(event["type"], str)
    assert "source" in event and isinstance(event["source"], str)
    assert "subject" in event and isinstance(event["subject"], str)
    assert "data" in event and isinstance(event["data"], dict)
    assert "id" in event and isinstance(event["id"], str)
    assert "message" in event["data"] and isinstance(event["data"]["message"], str)

    # Extract dataset ID from subject
    dataset_id = event["subject"].split(":")[-1]
    data_copy = {
        k: v
        for k, v in event["data"].items()
        if k not in ["message", "eventType", "eventSource", "datasetId"]
    }
    data_copy["source"] = event["source"]

    result_str = '{:<30} {:<8} type={:<46} msg="{}"'.format(
        event["time"],
        dataset_id,
        event["type"],
        event["data"]["message"],
    )
    if full:
        result_str += f" metadata={data_copy}"
    return result_str


@app.command("events")
def events(
    dataset_id: Annotated[
        str, typer.Argument(help="The dataset ID currently being processed.")
    ],
    watch: Annotated[
        bool, typer.Option("--watch", "-w", help='Watch for changes (like "tail -f")')
    ] = False,
    profile: Annotated[
        str,
        typer.Option(help="profile to use: dev, stg or prod."),
    ] = None,
    full: Annotated[
        bool,
        typer.Option("--full", "-f", help="Give extended information about the event."),
    ] = False,
):
    """
    Prints out the log messages for the dataset ID being processed.
    :param str dataset_id: The dataset ID currently being processed.
    :param bool watch: Watch for changes (like "tail -f").
    """
    assert dataset_id and isinstance(dataset_id, str)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    if not token:
        raise typer.Exit(1)

    previous_entry = None

    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset events",
        {"Dataset ID": dataset_id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    while True:
        url = (
            f"{get_control_plane_url(profile)}"
            f"/events?filter=datasetId.eq.{dataset_id}"
        )
        if previous_entry:
            url += "&limit=300"
        response = requests.get(
            url,
            headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            error_console.print(
                f'Failed to get events for {dataset_id}."'
                f' Error: {json.loads(response.text)["message"]}'
            )
            raise typer.Exit(1)
        returned_entries = response.json()
        # Results are returned in REVERSE TIME ORDER.
        print_all_entries = True
        if previous_entry is not None:
            # Find the matching entry starting at the end.
            match_index = 0
            for entry in returned_entries:
                if entry == previous_entry:
                    break
                match_index += 1
            if match_index < len(returned_entries):
                print_all_entries = False
                for entry in reversed(returned_entries[0:match_index]):
                    print(format_events_line(entry, full))
        if print_all_entries:
            for entry in reversed(returned_entries):
                print(format_events_line(entry, full))
        if not watch:
            break
        if returned_entries:
            previous_entry = returned_entries[0]
        else:
            previous_entry = None
        # Polling sucks but we can't stream with REST calls. Convert to something that
        # can stream like gRPC or websockets later.
        time.sleep(3)


def _get_curation_schemas(
    token, workflow, dataset_id, data_product_id, profile
) -> dict[str, dict[str, DeclaredField]]:
    """
    Get the latest curation event for the dataset and return the declared schema
    """
    # get latest declared schema from the curation event and update the ODIN dataset spec
    curation_schemas = dict()

    pipeline_ids = [pipeline.id for pipeline in workflow.pipelines]
    latest_curation_events = _get_latest_curation_events(
        token, dataset_id, data_product_id, pipeline_ids, profile
    )

    for event in latest_curation_events:
        frame_id = event["data"]["message"]["frameName"]
        declared_curation = event["data"]["message"]["declaredSpecs"]

        vendor_table_name = declared_curation["vendor_table_name"]
        vendor_table_description = declared_curation["vendor_table_description"]
        vendor_schedule = declared_curation["vendor_schedule"]
        fields = declared_curation["fields"]
        declared_fields = [DeclaredField(**field) for field in fields]
        version = "1.0"

        output = {
            "vendor_table_name": vendor_table_name,
            "vendor_table_description": vendor_table_description,
            "vendor_schedule": vendor_schedule,
            "version": version,
            "fields": fields,
        }
        declared_schema_def = DeclaredSchemaDef(**output)

        pipeline = workflow.get_pipeline(frame_id)
        pipeline.set_declared_schema_def(declared_schema_def)
        curation_schemas[pipeline.id] = _format_schemas(declared_fields)

    return curation_schemas


def _format_schemas(declared_fields: List[DeclaredField]) -> dict[str, DeclaredField]:
    curation_output = dict()
    for field in declared_fields:
        curation_output[field.name] = field
    return curation_output


@app.command("update")
def update(
    input_file: Annotated[
        Path, typer.Option("--file", "-f", help="Path to the ODIN dataset spec")
    ],
    profile: Annotated[
        str,
        typer.Option(help="profile to use: local, dev, staging, prod. Default: prod"),
    ] = None,
    from_docs: Annotated[
        bool,
        typer.Option(
            "--from-docs", "-fd", help="Update the dataset schema with vendor docs"
        ),
    ] = False,
    accept_all: Annotated[
        bool,
        typer.Option(
            help="Override all types in the ODIN dataset spec with the vendor declared schema"
        ),
    ] = False,
):
    """
    Fetches vendor declared schema from a vendors supplier documentation.
    Fills out 'Catalog' of the ODIN dataset spec with the vendor declared schema.
    Through interactive CLI, allows user to configure final type.
    """
    if not from_docs:
        return
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    with open(input_file, "r") as file:
        yaml_workflow_dict = yaml.safe_load(file)
        workflow = create_workflow(yaml_workflow_dict, do_validation=False)

    dataset_id = yaml_workflow_dict["metadata"]["dataset_id"]
    data_product_id = yaml_workflow_dict["metadata"]["data_product_id"]
    curation_schemas = _get_curation_schemas(
        token,
        workflow,
        dataset_id,
        data_product_id,
        profile,
    )

    configured_schemas = _configure_curation_schemas(
        workflow, curation_schemas, accept_all
    )
    for pipeline_id, schema_def in configured_schemas.items():
        pipeline = workflow.get_pipeline(pipeline_id)
        pipeline.set_schema_def(schema_def)

    workflow_dict = workflow.model_dump(exclude_none=True, exclude_unset=True)

    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset update",
        {
            "From Docs Used": from_docs,
            "Accept All Used": accept_all,
            "Dataset ID": dataset_id,
        },
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    with open(input_file, "w") as file:
        yaml.dump(workflow_dict, file)
    return


def _configure_curation_schemas(
    workflow: Workflow, curation_schemas: dict[str, Any], accept_all: bool
) -> dict[str, List]:
    # merge the declared schema with the existing schema
    configured_schemas = dict()
    schema_defs = workflow.get_all_pipeline_schema_defs()
    pipeline_ids = [pipeline.id for pipeline in workflow.pipelines]
    consolidated_dfs = _display_type_diffs(curation_schemas, schema_defs, pipeline_ids)

    for pipeline_id, df in consolidated_dfs.items():
        print(f"Resolving type differences for Pipeline: {pipeline_id}")
        resolved_df = _resolve_type_diffs(df, accept_all, pipeline_id)
        if not resolved_df:
            return
        configured_schemas[pipeline_id] = resolved_df
    return configured_schemas


def _check_uploaded_docs(
    token: str, dataset_id: str, data_product_id: str, profile: str
):
    url = f"{get_document_url(profile)}datasetId={dataset_id}"
    response = requests.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    returned_entries = response.json()
    if not returned_entries:
        print("No vendor documentation found for this dataset")
        redirect_url = (
            f"https://app.dev.cruxdata.com/data-products/"
            f"{data_product_id}/details/datasets/{dataset_id}/documentation"
        )
        print(f"Please upload the vendor documentation at: {redirect_url}")
        raise typer.Exit(code=1)


def _check_dataset_schema(
    token: str, dataset_id: str, data_product_id: str, profile: str
):
    url = f"{get_data_product_url(profile)}/{data_product_id}/datasets"
    response = requests.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    returned_entries = response.json()

    # check if dataset_id can be found from list of dataset_ids mapped to the data_product_id
    for entry in returned_entries:
        if entry["id"] == dataset_id:
            return

    print(
        "the dataset_id is not found for this product_id. Complete profiling schema at here"
    )
    redirect_url = f"https://app.dev.cruxdata.com/data-products/{data_product_id}/"
    print(f"Please complete profiling schema at: {redirect_url}")
    raise typer.Exit(code=1)


def _handle_no_curation_event(
    token: str, dataset_id: str, data_product_id: str, profile: str
):
    print(f"No curation event found for dataset: {dataset_id}")
    _check_dataset_schema(token, dataset_id, data_product_id, profile)
    _check_uploaded_docs(token, dataset_id, data_product_id, profile)
    raise typer.Exit(code=1)


def _get_latest_curation_events(
    token: str,
    dataset_id: str,
    data_product_id: str,
    pipeline_ids: List[str],
    profile: str,
) -> List[dict[str, Any]]:
    seen = set()
    latest_curation_event = []
    if not token:
        raise typer.Exit(1)

    url = (
        f"{get_control_plane_url(profile)}"
        f"/events?filter=subject.eq.crn:dataset:{dataset_id}"
    )
    print(url)
    response = requests.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    returned_entries = response.json()

    curation_events = []
    for event in returned_entries:
        if event["type"] == CURATION_EVENT_TYPE:
            curation_events.append(event)

    if not curation_events:
        _handle_no_curation_event(token, dataset_id, data_product_id, profile)
        raise typer.Exit(code=1)

    curation_events.sort(key=lambda x: x["time"], reverse=True)
    for event in curation_events:
        frame_name = event["data"]["message"]["frameName"]
        if frame_name in pipeline_ids and frame_name not in seen:
            seen.add(frame_name)
            latest_curation_event.append(event)
    print(latest_curation_event)
    return latest_curation_event


def _display_type_diffs(
    curation_schemas: dict[str, Any],
    yaml_schemas: dict[str, Any],
    pipeline_ids: List[str],
) -> dict[str, pd.DataFrame]:
    consolidated_dfs = dict()
    for idx, pipelind_id in enumerate(pipeline_ids):
        schema_def = yaml_schemas[idx]
        if pipelind_id in curation_schemas:
            curation_schema = curation_schemas[pipelind_id]
            consolidated_df = _consolidate_type_diffs_df(curation_schema, schema_def)
            consolidated_dfs[pipelind_id] = consolidated_df
    return consolidated_dfs


def _consolidate_type_diffs_df(
    curation_schema: dict[str, DeclaredField], yaml_schema: dict[str, Any]
) -> pd.DataFrame:
    yaml_columns = yaml_schema["fields"]
    yaml_column_names = [column["name"] for column in yaml_columns]
    consolidated = dict()

    for column in yaml_columns:
        column_name = column["name"]
        print(column_name)
        if column_name in curation_schema:
            curation_type = curation_schema[column_name].data_type
            consolidated[column_name] = [column["data_type"], curation_type]
        else:
            consolidated[column_name] = [column["data_type"], None]

    for curation_column in curation_schema.keys():
        if curation_column not in yaml_column_names:
            curation_type = curation_schema[curation_column].data_type
            consolidated[curation_column] = [None, curation_type]

    consolidated_df = pd.DataFrame.from_dict(
        consolidated,
        orient="index",
        columns=[SchemaClass.OBSERVED.value, SchemaClass.DECLARED.value],
    )
    return consolidated_df


def _resolve_type_diffs(
    consolidated_df: pd.DataFrame, accept_all: bool, pipeline_id: str
) -> List[dict[str, str]]:
    if consolidated_df is None or consolidated_df.empty:
        raise ValueError("Schema is empty. Exiting")
    console.print(consolidated_df)

    if accept_all:
        console.print(
            f"Overriding all types in the ODIN dataset spec for pipeline {pipeline_id}"
        )
        column_names = list(consolidated_df.index)
        resolved_types = list(consolidated_df[SchemaClass.DECLARED.value].values)

    else:
        column_names = list(consolidated_df.index)
        resolved_types = []
        for index, row in consolidated_df.iterrows():
            if row[SchemaClass.OBSERVED.value] == row[SchemaClass.DECLARED.value]:
                resolved_types.append(row[SchemaClass.OBSERVED.value])
                continue

            console.print(
                f"""Column Name: {index}
                | observed type: {row[SchemaClass.OBSERVED.value]}
                | declared type: {row[SchemaClass.DECLARED.value]}"""
                # noqa: E501
            )
            choice = typer.prompt(
                """Enter 1 to accept curation (DECLARED) type,
                2 to keep the existing (OBSERVED) type,
                3 for new type"""
                # noqa: E501
            )
            if int(choice) == 1:
                resolved_types.append(row[SchemaClass.DECLARED.value])
            elif int(choice) == 2:
                resolved_types.append(row[SchemaClass.OBSERVED.value])
            elif int(choice) == 3:
                new_type = typer.prompt("Enter the new type")
                resolved_types.append(new_type)
            else:
                new_type = typer.prompt("Enter the new type")
                resolved_types.append(new_type)

    configured_schema = []
    for column_name, resolved_type in zip(column_names, resolved_types):
        configured_schema.append(
            {"column_name": column_name, "data_type": resolved_type}
        )

    configured_df = pd.DataFrame(
        {SchemaClass.CONFIGURED.value: resolved_types}, index=column_names
    )
    resolved_df = pd.concat([consolidated_df, configured_df], axis=1)
    console.print(
        f"\nThis is configured schema based on your choices for pipeline: {pipeline_id}"
    )
    console.print(resolved_df)
    accept = typer.confirm("Do you accept this configured schema?")

    if accept:
        # Resolve the types
        console.print(
            f"Resolved types for pipeline: {pipeline_id}. Check the yaml for the update\n"
        )
        return configured_schema

    console.print(
        f"Not accepting the configured schema for pipeline: {pipeline_id}. Exiting\n"
    )
    raise typer.Abort()


def str_presenter(dumper, data):
    """
    Routine that puts quotes around strings that consist only of numbers but leaves
    everything else alone.
    """
    if re.compile("^[0-9]+$").match(data):
        if data == "08" or data == "09":
            data = re.sub("^0*", "", data)
        # If all digits, put quotes around it.
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


class ProfileValue(str, Enum):
    """
    Profile Value
    """

    local = "local"
    dev = "dev"
    staging = "stg"
    prod = "prod"


class ClusterValue(str, Enum):
    """
    Cluster Value
    """

    composer = "composer"
    oss = "oss"


class RegionValue(str, Enum):
    """
    Region Value
    """

    us_central1 = "us-central1"
    us_east1 = "us-east1"


class ShardValue(str, Enum):
    """
    Shard Value
    """

    zero = "0"
    one = "1"
    two = "2"
    three = "3"
    four = "4"
    five = "5"
    six = "6"
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"


class ApplyOdinParams(BaseModel):
    """
    Apply Odin Body
    """

    env: ProfileValue
    cluster: ClusterValue
    region: RegionValue
    shard: ShardValue

    class Config:
        use_enum_values = True


@app.command("apply")
def apply(
    file_list: Annotated[
        List[str],
        typer.Argument(
            help='File to apply or set of files to apply via a \
parent relationship if the files are separated by a comma. You can also give a directory \
as the first argument and a list of files below that directory to validate. It will look \
for matching parent or child files in that case. Example 1: "apply a.yaml b.yaml,c.yaml" \
- Apply a.yaml and combined b.yaml/c.yaml. Example 2: "apply ~/myyamls a.yaml c.yaml" - \
Apply a.yaml and c.yaml which exist below the directdory ~/myyamls. The command will \
search for the files a.yaml and c.yaml anywhere in the directory hierarchy below \
~/myyamls. In addition, suppose c.yaml has a "parent:" line pointing to b.yaml. Then \
b.yaml and c.yaml will be combined before they are applied.'
        ),
    ],
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet", "-q", help="Don't print out YAML files as they are applied."
        ),
    ] = False,
    profile: Annotated[
        ProfileValue,
        typer.Option(help="profile to use: local, dev, stg, prod. Default: prod"),
    ] = None,
    cluster: Annotated[
        ClusterValue,
        typer.Option(help="Airflow cluster to use: composer or oss. Default: oss"),
    ] = "oss",
    region: Annotated[
        RegionValue,
        typer.Option(
            help="Region to use: us-central1 or us-east1. Default: us-central1"
        ),
    ] = "us-central1",
    shard: Annotated[
        ShardValue,
        typer.Option(
            help="Shard to use: 0, 1, 2, 3, 4, 5, 6, a, b, c, d, e . Default: 0"
        ),
    ] = "a",
) -> None:
    """
    Apply an ODIN spec (possibly merged with its parent).

    :param Path start_directory: The directory to start looking for the YAML file and its parent.
    :param List[Path] yaml_files: The YAML file to apply (with an optional parent). This must
    be a file reference and not a path (relative or absolute).
    :param bool verbose: Print out YAML files as they are applied.
    """
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    if not token:
        raise typer.Exit(1)

    pathlib_list_of_list = parse_cmd_line_yaml_lists(file_list)
    for yaml_group in pathlib_list_of_list:
        dicts_to_coalesce = [yaml_file_to_dict(p) for p in yaml_group]
        dict_with_merged_yamls = MergeDicts(*dicts_to_coalesce)
        merged_dict_as_yaml = yaml.dump(dict(dict_with_merged_yamls))
        filename = os.path.basename(os.path.normpath(yaml_group[-1]))
        files = {
            "executionType": (None, "apply"),
            "file": (filename, merged_dict_as_yaml),
        }
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{get_control_plane_url(profile)}/apply"
        shard = "0" if not cluster or cluster == "composer" else shard
        structured_body = ApplyOdinParams(
            env=profile, cluster=cluster, region=region, shard=shard
        )
        params = structured_body.model_dump()
        # TODO: We use stg in cruxctl but staging in the /odin/apply call. Fix this.
        params["env"] = "staging" if profile == "stg" else profile
        # We are passing the ApplyOdinParams as query parameters but this isn't ideal.
        # We should pass it in the body. However, I'm not quite sure how to do this
        # since we are already passing the file and we are possibly going to redesign
        # this interface or go to a pubsub interface so we'll deal with that later.
        response = requests.post(url, files=files, params=params, headers=headers)
        dataset_name = dict_with_merged_yamls.get("id", "Unknown")
        mixpanel_token = get_mixpanel_token()
        if response.status_code not in [200, 201]:
            # I'm not sure why we get two different keys back when we get
            # an error. Maybe Python versus Java backends?
            track_mixpanel_event(
                "cruxctl dataset apply",
                {"Apply Result": False, "Dataset Name": dataset_name},
                api_token=token,
                mixpanel_token=mixpanel_token,
                profile=profile,
            )

            if "message" in response.text:
                message = json.loads(response.text)["message"]
            elif "detail" in response.text:
                message = json.loads(response.text)["detail"]
            else:
                message = response.text
            error_console.print(f"Failed to apply {yaml_group}. Error: {message}")
            raise typer.Exit(1)
        track_mixpanel_event(
            "cruxctl dataset apply",
            {"Apply Result": True, "Dataset Name": dataset_name},
            api_token=token,
            mixpanel_token=mixpanel_token,
            profile=profile,
        )
        if not quiet:
            console.print(f"Applied {yaml_group}")


@app.command("delete")
def delete(
    dataset_ids: Annotated[
        List[str],
        typer.Argument(help="Dataset ids to delete."),
    ],
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet", "-q", help="Don't print out dataset IDs aas they are printed."
        ),
    ] = False,
    profile: Annotated[
        str,
        typer.Option(help="profile to use: local, dev, staging, prod. Default: prod"),
    ] = None,
) -> None:
    """
    Deletes a set of dataset IDs.
    :param List[str] dataset_ids: The dataset IDs to delete.
    :param bool quiet: Don't print out dataset IDs as they are deleted.
    :param str profile: profile to use: local, dev, staging, prod. Default: prod.
    """
    assert (
        dataset_ids
        and isinstance(dataset_ids, list)
        and all(isinstance(s, str) for s in dataset_ids)
    )

    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    if not token:
        raise typer.Exit(1)

    for dataset_id in dataset_ids:
        url = f"{get_control_plane_url(profile)}/datasets/{dataset_id}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            error_console.print(
                f'Failed to delete {dataset_id}. Error: {json.loads(response.text)["message"]}'
            )
            raise typer.Exit(1)
        if not quiet:
            console.print(f"Deleted dataset ID {dataset_id}")


@app.command("validate")
def validate_yaml(
    file_list: Annotated[
        List[str],
        typer.Argument(
            help='File to validate or set of files to validate via \
parent relationship if the files are separated by a comma. You can also give a directory \
as the first argument and a list of files below that directory to validate. It will look \
for matching parent or child files in that case. Example 1: "validate a.yaml b.yaml,c.yaml" \
- Validate a.yaml and combined b.yaml/c.yaml. Example 2: "validate ~/myyamls a.yaml \
c.yaml" - Validate a.yaml and c.yaml which exist below the directory ~/myyamls. The \
command will search for the files a.yaml and c.yaml anywhere in the directory hierarchy \
below ~/myyamls. In addition, suppose c.yaml has a "parent:" line pointing to b.yaml. Then \
b.yaml and c.yaml will be combined before they are validated.'
        ),
    ],
    # This is opposite of what Unix commands usually do. When you do an "rm" or "cp"
    # Unix prints nothing. Unix usually only prints errors and is silent on success.
    # However, that isn't that useful here. People want feedback to know if the
    # validation succeeded.
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet", "-q", help="Don't print out YAML files as they are validated."
        ),
    ] = False,
    profile: Annotated[
        str,
        typer.Option(
            help="profile to use: local, dev, staging, prod. Default: prod."
            " This is only required when giving the --full option."
        ),
    ] = None,
    full: Annotated[
        bool,
        typer.Option(
            "--full",
            "-f",
            help="Run all validations including Crux specific custom validations."
            " This requires a call over the network to the control plane"
            " AND you have to give a profile environment.",
        ),
    ] = False,
) -> None:
    """
    Validate a YAML file (possibly merged with its parent). Since the parent and child
    YAML file can exist in separate directories, we give a start of the filesystem tree
    where to search for the YAML file and its parent.

    :param str start_directory: The directory to start looking for the YAML file and its parent.
    :param List[str] yaml_validation_files: The YAML files to validate (with an optional parent).
    These must be file references and not paths (relative or absolute).
    """
    assert (
        file_list
        and isinstance(file_list, list)
        and all(isinstance(s, str) for s in file_list)
    )

    pathlib_list_of_list = parse_cmd_line_yaml_lists(file_list)
    mixpanel_token = get_mixpanel_token()
    token = None
    if full:
        # token is necessary to call the POST request to do full validation.
        if not profile:
            profile = get_current_profile()
        token = set_api_token(console, profile)
        if not token:
            raise typer.Exit(1)
    for yaml_group in pathlib_list_of_list:
        dicts_to_coalesce = [yaml_file_to_dict(p) for p in yaml_group]
        dict_with_merged_yamls = MergeDicts(*dicts_to_coalesce)
        dataset_id = dict_with_merged_yamls.get("id", "Unknown")
        try:
            if full:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                url = f"{get_control_plane_url(profile)}/validate_odin_spec"
                response = requests.post(
                    url, headers=headers, json=dict_with_merged_yamls
                )
                if response.status_code not in [200, 201]:
                    error_console.print(
                        f'Failed to apply {yaml_group}."'
                        f' Error: {json.loads(response.text)["message"]}'
                    )
                    raise typer.Exit(1)
            else:
                validate_dict(dict_with_merged_yamls)
                custom_validations = CustomValidations(dict_with_merged_yamls)
                custom_validations.validate_all()
            if token:
                track_mixpanel_event(
                    "cruxctl dataset validate",
                    {"Validation Result": True, "Dataset ID": dataset_id},
                    api_token=token,
                    mixpanel_token=mixpanel_token,
                    profile=profile,
                )
            if not quiet:
                console.print(f"Validation passed for {yaml_group}")
        except jsonschema.ValidationError as ex:
            error_console.print(f"Validation failed for {yaml_group}: {ex}")
            if token:
                track_mixpanel_event(
                    "cruxctl dataset validate",
                    {"Validation Result": False, "Dataset ID": dataset_id},
                    api_token=token,
                    mixpanel_token=mixpanel_token,
                    profile=profile,
                )
            raise typer.Exit(1)
        except Exception as ex:
            error_console.print(f"Validation failed for {yaml_group}: {ex}")
            if token:
                track_mixpanel_event(
                    "cruxctl dataset validate",
                    {"Validation Result": False, "Dataset ID": dataset_id},
                    api_token=token,
                    mixpanel_token=mixpanel_token,
                    profile=profile,
                )
            raise typer.Exit(1)


CRUX_CONFIG_FILE = "config.yaml"


# @app.command("init")
def init(
    yaml_output_file: Annotated[
        Path,
        typer.Argument(help="What file to dump the new YAML file in"),
    ],
    version: Annotated[
        str,
        typer.Option(
            help="Workflow version. Currently unimplemented."
            " You currently always get the latest version."
        ),
    ] = "1.2.0",
    dataset_name: Annotated[
        str,
        typer.Option(help="Dataset name. If not given taken from output file name."),
    ] = "",
    data_product_name: Annotated[
        str,
        typer.Option(
            help="Data Product name. If not given taken from output file name."
        ),
    ] = "",
    profile: Annotated[
        str,
        typer.Option(help="profile to use: local, dev, staging, prod. Default: prod"),
    ] = None,
) -> None:
    """
    Create a new YAML file with the given dataset name.
    Args:
        version: Version of YAML file to create (default is latest 1.2.0).
        dataset_name: Name of the new dataset. This will be created in Crux.
        Default: from filename.
        data_product_name: Name of the new data product. This will be created in Crux.
        Default: from filename.
        yaml_output_file: The name of the output file to dump the YAML to.
        profile: profile to use: dev, staging, prod. Default: prod.

    Returns:
        None
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)
    if not token:
        raise typer.Exit(1)

    # Get payload to get the email then get the org ID.
    user_info = get_user_info_by_token(token, profile=profile)
    fetched_org_id = user_info["orgId"]
    console.print(f'Using org ID "{fetched_org_id}"')

    # See if data product is there. If not create it.
    file_path_basename = os.path.splitext(os.path.basename(yaml_output_file))[0]
    if not data_product_name:
        data_product_name = file_path_basename
    url = f"{get_url_based_on_profile(profile)}/catalog/data-products"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    params = {"filter": f"name.eq.{data_product_name}"}
    console.print(f'Checking if data product "{data_product_name}" exists')
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    if not response.json():
        console.print("It doesn't. Creating it.")
        body = {
            "name": f"{data_product_name}",
            "orgId": f"{fetched_org_id}",
            "subscriptionType": "EDP",
        }
        url = f'{get_url_based_on_profile(profile, version="v4")}/data-products'
        response = requests.post(url, headers=headers, json=body)
        if not 200 <= response.status_code <= 201:
            error_console.print(
                f'Error creating data product "{data_product_name}": {response.text}'
            )
            raise typer.Exit(1)
        data_product_id = response.json()["id"]
        console.print(
            f'Created data product "{data_product_name}" with ID "{data_product_id}"'
        )
    else:
        data_product_id = response.json()[0]["id"]
        console.print(
            f'Data product "{data_product_name}" with ID "{data_product_id}"'
            " already exists. Using it."
        )

    # Create the dataset
    if not dataset_name:
        dataset_name = file_path_basename
    url = f"{get_url_based_on_profile(profile)}/datasets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"name": dataset_name, "ownerIdentityId": fetched_org_id}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    dataset_id = response.json()["id"]
    console.print(f'Created dataset "{dataset_name}" with ID "{dataset_id}"')

    # We need to map the dataset id and data product id.
    url = (
        get_url_based_on_profile(profile, version="v4", swap_ops_version=True)
        + "/data-products/maps"
    )
    body = {"datasetId": dataset_id, "dataProductId": data_product_id}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    console.print(
        f'Mapped dataset "{dataset_name}" "{dataset_id}" to data product ID "{data_product_id}"'
    )

    # Get the Jinja2 template
    template_paths = ["templates", "cruxctl/templates"]
    with importlib.resources.as_file(
        importlib.resources.files(cruxctl) / "templates"
    ) as p:
        template_paths.append(str(p))
    env = Environment(
        loader=FileSystemLoader(template_paths), autoescape=select_autoescape()
    )
    template = env.get_template("dataset_init.yaml.j2")
    rendered_yaml = template.render(
        dataset_id=dataset_id, data_product_id=data_product_id, org_id=fetched_org_id
    )
    with open(yaml_output_file, "w") as f:
        f.write(rendered_yaml)
    console.print(f"Created {yaml_output_file}")


@app.command("run-dag")
def run_dag(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to run the DAG for."),
    ],
    dag_run_id: Annotated[
        str,
        typer.Option("--dag-run-id", "-d", help="A unique ID for the DAG run."),
    ],
    logical_date: Annotated[
        datetime,
        typer.Option(
            "--logical-date",
            "-l",
            formats=["%Y-%m-%dT%H:%M:%S"],
            help="The datetime to schedule the DAG run for.",
        ),
    ],
    note: Annotated[
        str, typer.Option("--note", "-n", help="Optional note for the DAG run.")
    ] = None,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Invokes a new DAG run for the provided dataset. This kicks off the run in the background. The
    actual execution status can be retrieved by querying the dataset events.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    try:
        mixpanel_token = get_mixpanel_token()
        track_mixpanel_event(
            "cruxctl dataset run-dag",
            {"Dataset ID": dataset_id, "Dag Run ID": dag_run_id},
            api_token=token,
            mixpanel_token=mixpanel_token,
            profile=profile,
        )
        DagRunHandler.run_dag(
            profile, token, dataset_id, dag_run_id, logical_date, note
        )
    except Exception as e:
        error_console.print(f"[red]Failed to invoke DAG run API: {e}[/red]")
        raise typer.Exit(code=1)

    console.print("[green]DAG run successfully invoked.[/green]")


@app.command("rerun-dag")
def rerun_dag(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to run the DAG for."),
    ],
    delivery_id: Annotated[
        str,
        typer.Argument(help="The delivery ID to rerun."),
    ],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="True if this is a dry rerun."),
    ] = False,
    only_failed: Annotated[
        bool,
        typer.Option("--only-failed", help="True to only rerun failed tasks."),
    ] = False,
    only_running: Annotated[
        bool,
        typer.Option(
            "--only-running", help="True to only rerun already running tasks."
        ),
    ] = False,
    task_ids: Annotated[
        List[str],
        typer.Option(
            "--task-id",
            help="The task ID to rerun. Multiple option definitions "
            "can be passed in. If none provided, all tasks will be rerun.",
        ),
    ] = None,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Invokes are DAG rerun for the provided dataset and run ID. This kicks off the rerun in the
    background. The actual execution status can be retrieved by querying the dataset events.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    try:
        mixpanel_token = get_mixpanel_token()
        track_mixpanel_event(
            "cruxctl dataset rerun-dag",
            {"Dataset ID": dataset_id, "Delivery ID": delivery_id},
            api_token=token,
            mixpanel_token=mixpanel_token,
            profile=profile,
        )
        DagRunHandler.rerun_dag(
            profile,
            token,
            dataset_id,
            delivery_id,
            dry_run,
            only_failed,
            only_running,
            task_ids,
        )
    except Exception as e:
        error_console.print(f"[red]Failed to invoke DAG rerun API: {e}[/red]")
        raise typer.Exit(code=1)

    console.print("[green]DAG rerun successfully invoked.[/green]")


@app.command("rerun-dispatch")
def rerun_dispatch(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to rerun the dispatch for."),
    ],
    export_activity_id: Annotated[
        str,
        typer.Option(
            "--export-activity-id",
            "-e",
            help="The matching export activity ID to rerun.",
        ),
    ],
    queue_key: Annotated[
        str,
        typer.Option("--queue-key", help="The queue for the rerun."),
    ] = DEFAULT_RERUN_QUEUE_KEY,
    export_activity_type: Annotated[
        ExportActivityType,
        typer.Option(
            "--export-activity-type", help="The export activity type to match."
        ),
    ] = ExportActivityType.SUCCESS,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Invokes are dispatch rerun for the provided dataset and export ID. This kicks off the rerun in
    the background. The actual execution status can be retrieved by querying the dataset events.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    try:
        mixpanel_token = get_mixpanel_token()
        track_mixpanel_event(
            "cruxctl dataset rerun-dispatch",
            {"Dataset ID": dataset_id},
            api_token=token,
            mixpanel_token=mixpanel_token,
            profile=profile,
        )
        DispatchRunHandler.rerun_dispatch(
            profile,
            token,
            dataset_id,
            export_activity_id,
            queue_key,
            export_activity_type,
        )
    except Exception as e:
        error_console.print(f"[red]Failed to invoke dispatch rerun API: {e}[/red]")
        raise typer.Exit(code=1)

    console.print("[green]Dispatch rerun successfully invoked.[/green]")


@app.command("smart-rerun")
def smart_rerun(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to rerun for."),
    ],
    delivery_id: Annotated[
        str,
        typer.Argument(help="The delivery ID to rerun."),
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Invokes a delivery rerun automatically based on the reported delivery failure type.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    try:
        mixpanel_token = get_mixpanel_token()
        track_mixpanel_event(
            "cruxctl dataset smart-rerun",
            {"Dataset ID": dataset_id, "Delivery ID": delivery_id},
            api_token=token,
            mixpanel_token=mixpanel_token,
            profile=profile,
        )

        DagRunHandler.smart_rerun_dag(profile, token, dataset_id, delivery_id)
    except Exception as e:
        error_console.print(f"[red]Failed to invoke smart rerun API: {e}[/red]")
        raise typer.Exit(code=1)

    console.print("[green]Smart rerun successfully invoked.[/green]")


@app.command("dispatch-logs")
def get_dispatch_logs(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to get dispatch logs."),
    ],
    export_id: Annotated[
        str,
        typer.Option(
            "--export-id",
            "-e",
            help="Export ID to filter logs (dispatch only)",
        ),
    ],
    profile: Annotated[
        str,
        typer.Option(help="profile to use: local, dev, staging, prod. Default: prod"),
    ] = None,
    delivery_id: Annotated[
        str,
        typer.Option("--delivery-id", "-d", help="Delivery ID to filter logs"),
    ] = None,
    page_size: Annotated[
        int,
        typer.Option("--page-size", help="Page size to limit logs"),
    ] = 100,
):
    """
    Retrieves dispatch logs for the provided dataset based on filter criteria.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    mixpanel_token = get_mixpanel_token()
    track_mixpanel_event(
        "cruxctl dataset logs",
        {"Dataset ID": dataset_id},
        api_token=token,
        mixpanel_token=mixpanel_token,
        profile=profile,
    )

    filter_criteria = {
        "exportId": export_id,
        "deliveryId": delivery_id,
    }

    get_logs_with_pagination(
        profile, token, dataset_id, "dispatch", filter_criteria, page_size
    )


@app.command("pdk-logs")
def get_logs(
    dataset_id: Annotated[
        str,
        typer.Argument(help="The dataset ID to get PDK logs."),
    ],
    delivery_id: Annotated[
        str,
        typer.Option("--delivery-id", "-d", help="Delivery ID to filter PDK logs"),
    ],
    profile: Annotated[
        str,
        typer.Option(help="profile to use: local, dev, staging, prod. Default: prod"),
    ] = None,
    schedule_date: Annotated[
        str,
        typer.Option("--schedule-date", "-sd", help="Schedule date to filter PDK logs"),
    ] = None,
    page_size: Annotated[
        int,
        typer.Option("--page-size", help="Page size to limit logs"),
    ] = 100,
):
    """
    Retrieves PDK logs for the provided dataset based on filter criteria.
    """
    if not profile:
        profile = get_current_profile()
    token: str = set_api_token(console, profile)
    if not token:
        raise typer.BadParameter("Failed to read Crux API token")

    filter_criteria = {
        "scheduleDate": schedule_date,
        "deliveryId": delivery_id,
    }

    get_logs_with_pagination(
        profile, token, dataset_id, "pdk", filter_criteria, page_size
    )


def get_logs_with_pagination(
    profile: str,
    token: str,
    dataset_id: str,
    type: str,
    filter_criteria: dict,
    page_size: int,
):
    """
    Helper function to retrieve logs with pagination, and print log entries.
    """
    page_token = ""
    while True:
        try:
            # Make the API call with the filter criteria and pagination
            response = LogsHandler.get_logs(
                profile,
                token,
                dataset_id,
                type,
                **filter_criteria,
                page_token=page_token,
                page_size=page_size,
            )

            # Process the log entries
            if "entries" in response and response["entries"]:
                for entry in response["entries"]:
                    entry_time = entry.get("timestamp", "No timestamp available")
                    text_payload = entry.get("textPayload", None)
                    console.print(f"[{entry_time}] {text_payload}")
            else:
                console.print("No logs available for last 30 days.")

            # Pagination handling
            next_page_token = response.get("nextPageToken", None)
            if next_page_token:
                user_input = input("Press Enter to load the next page or 'q' to quit: ")
                if user_input.lower() == "q":
                    break
                page_token = next_page_token
            else:
                console.print("No more pages available.")
                break

        except Exception as e:
            error_console.print(f"[red]Failed to invoke logs API: {e}[/red]")
            raise typer.Exit(code=1)
