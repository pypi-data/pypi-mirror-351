from datetime import datetime

import requests

from cruxctl.common.utils.api_utils import (
    get_control_plane_url,
    get_api_headers,
    raise_for_status,
)

DEFAULT_API_TIMEOUT_SECONDS: int = 10
DEFAULT_CLOUD_EVENT_SOURCE: str = "cruxctl"


class DagRunHandler:
    @staticmethod
    def run_dag(
        profile: str,
        api_token: str,
        dataset_id: str,
        dag_run_id: str,
        logical_date: datetime,
        note: str,
    ) -> None:
        """
        Calls the control plane API to run a DAG for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to run
        :param dag_run_id: user specified DAG run ID
        :param logical_date: the datetime at which to schedule the DAG run
        :param note: optional note to attach to the DAG run
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/run"

        headers: dict = get_api_headers(api_token)
        headers["source"] = DEFAULT_CLOUD_EVENT_SOURCE

        logical_date_str: str = logical_date.strftime("%Y-%m-%dT%H:%M:%S")

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "dagRunId": dag_run_id,
                "logicalDate": logical_date_str,
                "note": note,
            },
        )

        raise_for_status(response)

    @staticmethod
    def rerun_dag(
        profile: str,
        api_token: str,
        dataset_id: str,
        delivery_id: str,
        dry_run: bool = False,
        only_failed: bool = False,
        only_running: bool = False,
        task_ids: list[str] = None,
    ) -> None:
        """
        Calls the control plane API to rerun a DAG for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to rerun
        :param delivery_id: the delivery ID to rerun
        :param dry_run: whether to perform a dry run
        :param only_failed: whether to only run failed tasks
        :param only_running: whether to only run running tasks
        :param task_ids: list of task IDs to run
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/rerun"

        headers: dict = get_api_headers(api_token)
        headers["source"] = DEFAULT_CLOUD_EVENT_SOURCE

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "deliveryId": delivery_id,
                "dryRun": dry_run,
                "onlyFailed": only_failed,
                "onlyRunning": only_running,
                "taskIds": task_ids,
            },
        )

        raise_for_status(response)

    @staticmethod
    def smart_rerun_dag(
        profile: str,
        api_token: str,
        dataset_id: str,
        delivery_id: str,
    ) -> None:
        """
        Calls the control plane API to smart rerun a DAG for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to rerun
        :param delivery_id: the delivery ID to rerun
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/deliveries/{delivery_id}/rerun"

        headers: dict = get_api_headers(api_token)
        headers["source"] = DEFAULT_CLOUD_EVENT_SOURCE

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
        )

        raise_for_status(response)
