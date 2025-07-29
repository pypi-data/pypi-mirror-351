import csv
import json

import requests
from requests import HTTPError

from cruxctl.common.models.application_profile import ApplicationProfile
from cruxctl.common.data_adapters import json_to_rich_table
from cruxctl.common.models.data_format import DataFormat
from cruxctl.common.models.file_frequency import FileFrequency
from cruxctl.common.utils.api_utils import (
    MAX_PAGE_SIZE,
    get_url_based_on_profile,
    get_control_plane_url,
)

DEFAULT_API_TIMEOUT_SECONDS = 50
DEADLINE_RECOMMENDATION_EVENT_TYPE = (
    "com.crux.cp.schedule.deadline-recommendation.success.v1"
)


class DeadlineRecommendationClient:
    """
    A client for querying recommended deadlines
    """

    def get_recommended_deadline(self, profile: str, token: str, dataset_id: str):
        url = (
            f"{get_control_plane_url(profile)}"
            f"/events?filter=subject.eq.crn:dataset:{dataset_id}"
        )
        response = requests.get(
            url,
            headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        returned_entries = response.json()
        entry_subject = f"crn:dataset:{dataset_id}"
        latest_entry = max(
            (
                entry
                for entry in returned_entries
                if entry.get("type") == DEADLINE_RECOMMENDATION_EVENT_TYPE
                and entry.get("subject") == entry_subject
            ),
            key=lambda x: x.get("time"),
            default=None,
        )
        deadline = latest_entry["data"] if latest_entry is not None else None
        return deadline


class DatasetDeadlineClient:
    """
    A client for handling dataset deadlines.
    """

    def get_all_deadlines(
        self,
        profile: str,
        token: str,
        dataset_id: str = None,
        limit: int = 100,
        output_format: DataFormat = None,
    ):
        """
        Retrieves all deadlines for a given dataset.

        Args:
            profile (str): The application profile.
            token (str): The authorization token.
            dataset_id (str, optional): The ID of the dataset. Defaults to None.
            output_format ([type], optional): The output format. Defaults to None.
            limit (int, optional): The limit of deadlines to retrieve. Defaults to 100.
        """
        path = "/datasets/deadlines/search"
        url = get_url_based_on_profile(profile) + path
        all_deadlines = []

        if limit < 0 or limit > MAX_PAGE_SIZE:
            limit = MAX_PAGE_SIZE

        if not dataset_id:
            payload = {}
        else:
            payload = {"datasetId": dataset_id}

        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }
        page_number = 0

        while True:
            page_size = limit if 100 > limit else 100
            querystring = {"pageNumber": str(page_number), "pageSize": str(page_size)}

            response = requests.request(
                "POST",
                url,
                json=payload,
                headers=headers,
                params=querystring,
                timeout=DEFAULT_API_TIMEOUT_SECONDS,
            )

            try:
                self.raise_for_status(response)
            except HTTPError as ex:
                print(f"Error making api request: {ex}")
                break

            decoded_content = response.content.decode("utf-8")

            if decoded_content == "[]":
                break
            deadline_list = json.loads(decoded_content)
            for deadline in deadline_list:
                if "dataset" in deadline and deadline["dataset"] is not None:
                    deadline["workflowId"] = deadline["dataset"]["workflowId"]
                    deadline.pop("dataset")

            all_deadlines.extend(deadline_list)
            page_number += 1
            limit = limit - page_size
            if limit <= 0:
                break

        if output_format == DataFormat.table:
            return json_to_rich_table(all_deadlines)
        return all_deadlines

    def upsert_deadline(
        self,
        profile: str,
        token: str,
        dataset_id: str,
        deadline_minute: str,
        deadline_hour: str,
        deadline_day_of_the_month: str,
        deadline_month: str,
        deadline_day_of_week: str,
        file_frequency: FileFrequency,
        timezone: str = "UTC",
        is_active: bool = True,
        is_excluded: bool = False,
        delete_if_exists: bool = True,
    ):
        """
        Inserts a new deadline for a given dataset.

        Args:
            profile (str): The application profile.
            token (str): The authorization token.
            dataset_id (str): The ID of the dataset.
            deadline_minute (str): The minute of the deadline.
            deadline_hour (str): The hour of the deadline.
            deadline_day_of_the_month (str): The day of the month of the deadline.
            deadline_month (str): The month of the deadline.
            deadline_day_of_week (str): The day of the week of the deadline.
            deadline_year (str): The year of the deadline.
            file_frequency (str): The frequency of the file.
            timezone (str, optional): The timezone of the deadline. Defaults to None.
            is_active (bool, optional): Whether the dataset is active. Defaults to True.
            is_excluded (bool, optional): Whether the dataset is excluded in Zendesk Exclusions.
              Defaults to False.
            delete_if_exists (bool, optional): Whether to delete any existing dataset deadlines
            first.
        """
        path = "/datasets/deadlines/bulk"
        url = (
            f"{get_url_based_on_profile(profile)}{path}"
            f"?deleteExisting={str(delete_if_exists).lower()}"
        )

        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }

        payload = [
            {
                "datasetId": dataset_id,
                "deadlineMinute": deadline_minute,
                "deadlineHour": deadline_hour,
                "deadlineDayOfTheMonth": deadline_day_of_the_month,
                "deadlineMonth": deadline_month,
                "deadlineDayOfWeek": deadline_day_of_week,
                "deadlineYear": "*",
                "timezone": timezone,
                "fileFrequency": file_frequency.value,
                "active": is_active,
                "excluded": is_excluded,
            }
        ]

        response = requests.request(
            "PUT",
            url,
            json=payload,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
        )
        self.raise_for_status(response)

    def delete_deadline_by_id(self, profile: str, token: str, deadline_id: str):
        """
        Deletes a deadline by its ID.

        Args:
            profile (str): The application profile.
            token (str): The authorization token.
            deadline_id (str): The ID of the dataset deadline to delete.
        """
        path = f"/datasets/deadlines/{deadline_id}"
        url = get_url_based_on_profile(profile) + path

        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }

        response = requests.request(
            "DELETE", url, headers=headers, timeout=DEFAULT_API_TIMEOUT_SECONDS
        )
        self.raise_for_status(response)

    def bulk_insert_deadlines(self, profile: str, token: str, file_path: str):
        """
        Bulk inserts deadlines from a CSV file.

        Args:
            profile (str): The application profile.
            token (str): The authorization token.
            file_path (str): The path to the CSV file.
        """
        path = "/datasets/deadlines/bulk-create"
        url = get_url_based_on_profile(profile) + path

        headers = {"accept": "*/*", "Authorization": "Bearer " + token}

        with open(file_path, "r") as file:
            # Read the CSV file and convert each row into a dictionary
            reader = csv.DictReader(file)
            data = list(reader)
        response = requests.request(
            "POST", url, headers=headers, json=data, timeout=DEFAULT_API_TIMEOUT_SECONDS
        )
        self.raise_for_status(response)

    def export_to_local_file(
        self, profile: ApplicationProfile, file_path: str, token: str
    ):
        """
        Exports all deadlines to a local CSV file.

        Args:
            profile (str): The application profile.
            file_path (str): The path to the CSV file.
            token(str): The authorization token.
        """
        all_deadlines = self.get_all_deadlines(
            profile, token=token, output_format=DataFormat.json, limit=-1
        )
        with open(file_path, "w") as file:
            writer = csv.DictWriter(file, fieldnames=all_deadlines[0].keys())
            writer.writeheader()
            writer.writerows(all_deadlines)

    def delete_deadlines_from_csv(self, profile: str, token: str, file_path: str):
        """
        Deletes deadlines from a CSV file by record ID.

        Args:
            profile (str): The application profile.
            token (str): The authorization token.
            file_path (str): The path to the CSV file.
        """
        with open(file_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.delete_deadline_by_id(profile, token, row["id"])

    @staticmethod
    def raise_for_status(response):
        """
        Raises `HTTPError` if one occurred.
        Checks the response for an error status and raises an exception with the error
        message provided by the server.
        :param response:
        :return:
        """

        if 400 <= response.status_code < 600:
            if isinstance(response.reason, bytes):
                try:
                    reason = response.reason.decode("utf-8")
                except UnicodeDecodeError:
                    reason = response.reason.decode("iso-8859-1")
            else:
                reason = response.reason

            raise HTTPError(
                f"{response.status_code} {reason} -> ({response.text}) for url: {response.url}",
                response=response,
            )
