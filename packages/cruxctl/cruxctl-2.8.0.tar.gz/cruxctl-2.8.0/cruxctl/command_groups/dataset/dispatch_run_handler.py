import requests

from cruxctl.command_groups.dataset.models.export_activity_type import (
    ExportActivityType,
)
from cruxctl.common.utils.api_utils import (
    get_control_plane_url,
    get_api_headers,
    raise_for_status,
)

DEFAULT_API_TIMEOUT_SECONDS: int = 10
DEFAULT_CLOUD_EVENT_SOURCE: str = "cruxctl"
DEFAULT_RERUN_QUEUE_KEY: str = "ongoing"


class DispatchRunHandler:
    @staticmethod
    def rerun_dispatch(
        profile: str,
        api_token: str,
        dataset_id: str,
        export_activity_id: str,
        queue_key: str = DEFAULT_RERUN_QUEUE_KEY,
        export_activity_type: ExportActivityType = ExportActivityType.SUCCESS,
    ) -> None:
        """
        Calls the control plane API to rerun a dispatch for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to rerun
        :param export_activity_id: the export activity ID to rerun
        :param queue_key: the queue key to match
        :param export_activity_type: the export activity type to match
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/dispatch/rerun"

        headers: dict = get_api_headers(api_token)
        headers["source"] = DEFAULT_CLOUD_EVENT_SOURCE

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "exportActivityId": export_activity_id,
                "queueKey": queue_key,
                "exportActivityType": export_activity_type.value,
            },
        )

        raise_for_status(response)
