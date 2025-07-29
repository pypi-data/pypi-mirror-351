import json
from datetime import datetime

import requests
from requests import HTTPError
from rich.table import Table

from cruxctl.command_groups.deadlines.models.deadline_notification_snooze_units import (
    DeadlineNotificationSnoozeUnits,
)
from cruxctl.common.data_adapters import json_to_rich_table
from cruxctl.common.models.data_format import DataFormat
from cruxctl.common.utils.api_utils import (
    get_api_headers,
    get_url_based_on_profile,
    raise_for_status,
    MAX_PAGE_SIZE,
)

DEFAULT_API_TIMEOUT_SECONDS: int = 50


class DatasetSnoozeClient:
    """
    A client for handling dataset snoozes.
    """

    @staticmethod
    def get_all_notification_snooze(
        profile: str,
        api_token: str,
        sort_by: str = None,
        limit: int = 50,
        filters: str = None,
        pagination_token: str = None,
        output_format: DataFormat = None,
    ) -> Table | dict:
        """
        Retrieves all snoozes from the database, paginated.
        :param pagination_token: (str): The token for pagination.
        :param profile: (str): The application profile.
        :param api_token: (str): The authorization token
        :param sort_by: (str): String specifying sort preference.
        :param limit: (int): The maximum of snoozes to retrieve. Defaults to 50.
        :param filters: (str): String specifying filter preference.
        :param output_format: (DataFormat): The output format of the data.
        :return:
        """
        path: str = "/datasets/snoozes"
        url: str = get_url_based_on_profile(profile) + path

        if limit < 0 or limit > MAX_PAGE_SIZE:
            limit = MAX_PAGE_SIZE

        headers: dict = get_api_headers(api_token)

        while True:
            querystring = {
                "pageSize": str(limit),
                "filters": filters,
                "sortBy": sort_by,
                "pageToken": pagination_token,
            }

            response = requests.request(
                method="GET",
                url=url,
                headers=headers,
                params=querystring,
                timeout=DEFAULT_API_TIMEOUT_SECONDS,
            )

            try:
                raise_for_status(response)
            except HTTPError as ex:
                print(f"Error making api request: {ex}")
                break

            decoded_content = response.content.decode("utf-8")

            if decoded_content == "[]":
                break

            paginated_snooze_list: dict = json.loads(decoded_content)

            snoozes: list = paginated_snooze_list.get("items", [])
            next_page_token = paginated_snooze_list.get("nextPageToken", None)

            if next_page_token is None:
                break
            else:
                pagination_token = next_page_token

        if output_format == DataFormat.table:
            return json_to_rich_table(snoozes)
        else:
            return paginated_snooze_list

    @staticmethod
    def get_notification_snooze_by_dataset_id(
        profile: str,
        output_format: DataFormat,
        api_token: str,
        dataset_id: str,
    ) -> Table | list:
        path: str = f"/datasets/{dataset_id}/snoozes"
        url: str = get_url_based_on_profile(profile) + path
        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="GET",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
        )

        try:
            raise_for_status(response)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                return json_to_rich_table([])
            print(f"Error making api request: {ex}")

        decoded_content = response.content.decode("utf-8")
        snoozes: list = json.loads(decoded_content)

        if len(snoozes) != 0 and output_format == DataFormat.table:
            return json_to_rich_table(snoozes)
        else:
            return snoozes

    @staticmethod
    def insert_notification_snooze(
        profile: str,
        api_token: str,
        dataset_id: str,
        snooze_duration: int,
        snooze_units: DeadlineNotificationSnoozeUnits,
        snooze_start_time: datetime = None,
    ) -> None:
        path: str = f"/datasets/{dataset_id}/snoozes"
        url: str = get_url_based_on_profile(profile) + path
        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "snoozeDuration": snooze_duration,
                "snoozeUnits": snooze_units,
                "snoozeStartTime": snooze_start_time,
            },
        )

        try:
            raise_for_status(response)
        except HTTPError as ex:
            print(f"Error making api request: {ex}")

    @staticmethod
    def delete_notification_snooze_by_dataset_id(
        profile: str, api_token: str, dataset_id: str
    ) -> None:
        path: str = f"/datasets/{dataset_id}/snoozes"
        url: str = get_url_based_on_profile(profile) + path
        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="DELETE",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
        )

        try:
            raise_for_status(response)
        except HTTPError as ex:
            print(f"Error making api request: {ex}")

    @staticmethod
    def delete_expired_notification_snoozes(profile: str, api_token: str) -> None:
        path: str = "/datasets/snoozes/expired"
        url: str = get_url_based_on_profile(profile) + path
        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="DELETE",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
        )

        try:
            raise_for_status(response)
        except HTTPError as ex:
            print(f"Error making api request: {ex}")

    @staticmethod
    def update_notification_snooze(
        profile: str,
        api_token: str,
        dataset_id: str,
        snooze_id: str,
        snooze_duration: int,
        snooze_units: DeadlineNotificationSnoozeUnits,
        snooze_start_time: datetime = None,
    ) -> None:
        path: str = f"/datasets/{dataset_id}/snoozes/{snooze_id}"
        url: str = get_url_based_on_profile(profile) + path
        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="PUT",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "snoozeDuration": snooze_duration,
                "snoozeUnits": snooze_units,
                "snoozeStartTime": snooze_start_time,
            },
        )

        try:
            raise_for_status(response)
        except HTTPError as ex:
            print(f"Error making api request: {ex}")
