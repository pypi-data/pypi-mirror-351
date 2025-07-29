import requests

from cruxctl.common.utils.api_utils import (
    get_control_plane_url,
    get_api_headers,
    raise_for_status,
)

DEFAULT_API_TIMEOUT_SECONDS: int = 10


class LogsHandler:
    @staticmethod
    def get_logs(
        profile: str,
        api_token: str,
        dataset_id: str,
        type: str,
        page_token: str,
        page_size: int,
        **filter_criteria: dict,
    ) -> dict:
        """
        Calls the control plane API to retrieve logs for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to get logs for
        :param type: pdk or dispatch
        :param page_token: Optional page token for next page of logs
        :param page_size: Optional page size for logs
        :param filter_criteria: A dictionary of optional filter parameters like
                                 export_id, execution_date, delivery_id, cdu_id.
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/logs/{type}"

        headers: dict = get_api_headers(api_token)

        # Building the request body dynamically based on the passed filter_criteria
        request_body = {
            "datasetId": dataset_id,
            "pageToken": page_token,
            "pageSize": page_size,
            "orderBy": "timestamp desc",
        }

        # Add the filter criteria if they are provided
        for key, value in filter_criteria.items():
            if value is not None:
                request_body[key] = value

        # Making the POST request
        response = requests.post(
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json=request_body,
        )

        raise_for_status(response)
        return response.json()
