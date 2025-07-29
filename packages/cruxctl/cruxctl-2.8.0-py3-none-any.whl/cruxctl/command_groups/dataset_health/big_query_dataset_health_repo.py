from datetime import date
from typing import Callable

from google.cloud import bigquery

from cruxctl.command_groups.dataset_health.models.dataset_health_profile import (
    get_postgres_database,
    get_processing_health_table,
    get_dispatch_health_table,
    get_aggregated_by_dataset_status_view,
    get_aggregated_by_subscriber_status_view,
)
from cruxctl.common.utils.sql_utils import get_limit_expression


NOTIFICATION_HISTORY_TABLE = "delivery_recon.dataset_notification_history"


class BiqQueryDatasetHealthRepo:
    def __init__(self):
        self.client = bigquery.Client()

    def get_all_processing_health(
        self,
        profile: str,
        data_adapter: Callable,
        delivery_deadline_date: date,
        limit: int = 100,
    ):
        limit_expression = get_limit_expression(limit)
        where_expression = self.get_deadline_matches_date_expression(
            delivery_deadline_date
        )

        database = get_postgres_database(profile)
        table = get_processing_health_table(profile)

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT dataset_id, '
            f"workflow_id, "
            f"delivery_deadline, "
            f"CAST(status AS TEXT), "
            f"delivery_id, "
            f"cdu_id, "
            f"scheduled_run, "
            f"{self._get_flattened_deadline_config_expression()}, "
            f"message, "
            f"CAST(created_at AS TEXT), "
            f"CAST(modified_at AS TEXT) "
            f"FROM {table} "
            f"{where_expression}"
            f"ORDER BY delivery_deadline DESC"
            f'{limit_expression};");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def _get_flattened_deadline_config_expression(self):
        return (
            "delivery_deadline_config->>'deadline_minute' AS deadline_minute, "
            "delivery_deadline_config->>'deadline_hour' AS deadline_hour, "
            "delivery_deadline_config->>'deadline_day_of_the_month' AS deadline_day_of_the_month, "
            "delivery_deadline_config->>'deadline_month' AS deadline_month, "
            "delivery_deadline_config->>'deadline_day_of_week' AS deadline_day_of_week, "
            "delivery_deadline_config->>'deadline_year' AS deadline_year, "
            "delivery_deadline_config->>'timezone' AS timezone"
        )

    def get_deadline_matches_date_expression(self, delivery_deadline_date: date) -> str:
        return (
            f"WHERE delivery_deadline::date = '{delivery_deadline_date}' "
            if delivery_deadline_date
            else ""
        )

    def get_processing_health_by_dataset_id(
        self,
        profile: str,
        data_adapter: Callable,
        dataset_id: str,
        delivery_deadline_date: date,
    ):
        database = get_postgres_database(profile)
        table = get_processing_health_table(profile)
        delivery_deadline_expression = (
            f" AND delivery_deadline::date = '{delivery_deadline_date}' "
            if delivery_deadline_date
            else ""
        )

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT dataset_id, '
            f"workflow_id, "
            f"delivery_deadline, "
            f"CAST(status AS TEXT), "
            f"delivery_id, "
            f"cdu_id, "
            f"scheduled_run, "
            f"{self._get_flattened_deadline_config_expression()}, "
            f"message, "
            f"CAST(created_at AS TEXT), "
            f"CAST(modified_at AS TEXT) "
            f"FROM {table} "
            f"WHERE dataset_id = '{dataset_id}'{delivery_deadline_expression} "
            f'ORDER BY delivery_deadline DESC;");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def get_all_dispatch_health(
        self,
        profile: str,
        data_adapter: Callable,
        delivery_deadline_date: date,
        limit: int = 100,
    ):
        limit_expression = get_limit_expression(limit)
        where_expression = self.get_deadline_matches_date_expression(
            delivery_deadline_date
        )

        database = get_postgres_database(profile)
        table = get_dispatch_health_table(profile)

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT dataset_id, '
            f"subscription_id, "
            f"delivery_deadline, "
            f"delivery_id, "
            f"subscriber_id, "
            f"cdu_id, "
            f"CAST(status AS TEXT), "
            f"{self._get_flattened_deadline_config_expression()}, "
            f"message, "
            f"CAST(created_at AS TEXT), "
            f"CAST(modified_at AS TEXT) "
            f"FROM {table} "
            f"{where_expression} "
            f"ORDER BY delivery_deadline DESC"
            f'{limit_expression};");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def get_dispatch_health(
        self,
        profile: str,
        data_adapter: Callable,
        dataset_id: str,
        subscriber_id: str,
        delivery_deadline_date: date,
    ):
        database = get_postgres_database(profile)
        table = get_dispatch_health_table(profile)

        where_expression = self._get_dataset_health_where_expression(
            dataset_id, subscriber_id, delivery_deadline_date
        )

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT dataset_id, '
            f"subscription_id, "
            f"delivery_deadline, "
            f"delivery_id, "
            f"subscriber_id, "
            f"cdu_id, "
            f"CAST(status AS TEXT), "
            f"{self._get_flattened_deadline_config_expression()}, "
            f"message, "
            f"CAST(created_at AS TEXT), "
            f"CAST(modified_at AS TEXT) "
            f"FROM {table} "
            f"{where_expression} "
            f'ORDER BY delivery_deadline DESC;");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def _get_dataset_health_where_expression(
        self, dataset_id: str, subscriber_id: str, delivery_deadline_date: date
    ) -> str:
        if not dataset_id and not subscriber_id and not delivery_deadline_date:
            return ""

        conditions = []

        if dataset_id:
            conditions.append(f" dataset_id = '{dataset_id}'")

        if subscriber_id:
            conditions.append(f" subscriber_id = '{subscriber_id}' ")

        if delivery_deadline_date:
            conditions.append(f" delivery_deadline::date = '{delivery_deadline_date}'")

        return f"WHERE {' AND '.join(conditions)}"

    def get_dataset_health_grouped_by_dataset(
        self,
        profile: str,
        data_adapter: Callable,
        dataset_id: str,
        subscriber_id: str,
        delivery_deadline_date: date,
    ):
        database = get_postgres_database(profile)
        view = get_aggregated_by_dataset_status_view(profile)

        where_expression = self._get_aggregated_by_dataset_health_where_expression(
            dataset_id, subscriber_id, delivery_deadline_date
        )

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT dataset_id, '
            f"delivery_deadline, "
            f"processing_status::text, "
            f"dispatch_statuses::text[], "
            f"aggregated_status::text, "
            f"subscription_ids::text[], "
            f"subscribers "
            f"FROM {view} "
            f'{where_expression};");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def _get_aggregated_by_dataset_health_where_expression(
        self, dataset_id: str, subscriber_id: str, delivery_deadline_date: date
    ) -> str:
        if not dataset_id and not subscriber_id and not delivery_deadline_date:
            return ""

        conditions = []

        if dataset_id:
            conditions.append(f" dataset_id = '{dataset_id}'")

        if subscriber_id:
            conditions.append(f" '{subscriber_id}' = ANY (subscribers) ")

        if delivery_deadline_date:
            conditions.append(f" delivery_deadline::date = '{delivery_deadline_date}'")

        return f"WHERE {' AND '.join(conditions)}"

    def get_dataset_health_grouped_by_subscriber(
        self,
        profile: str,
        data_adapter: Callable,
        dataset_id: str,
        subscriber_id: str,
        delivery_deadline_date: date,
    ):
        database = get_postgres_database(profile)
        view = get_aggregated_by_subscriber_status_view(profile)

        where_expression = self._get_dataset_health_where_expression(
            dataset_id, subscriber_id, delivery_deadline_date
        )

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            f'"SELECT subscriber_id, '
            f"dataset_id, "
            f"delivery_deadline, "
            f"processing_status::text, "
            f"dispatch_statuses::text[], "
            f"aggregated_status::text, "
            f"subscription_ids::text[]"
            f"FROM {view} "
            f'{where_expression};");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def get_all_notification_history(
        self, profile: str, data_adapter: Callable, limit: int = 100
    ):
        limit_expression = get_limit_expression(limit)

        database = get_postgres_database(profile)

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            '"SELECT CAST(id AS VARCHAR), dataset_id, CAST(delivery_deadline AS VARCHAR), '
            "cast(notification_type as VARCHAR), CAST(created_at AS VARCHAR), "
            "CAST(modified_at AS VARCHAR), "
            "notification_payload->>'file_frequency' as file_frequency, "
            "notification_payload->>'v2_dataset_id' as v2_dataset_id, "
            "notification_payload->>'delivery_mins_late' as delivery_mins_late, "
            "notification_payload->>'most_recent_delivery_time' as most_recent_delivery_time, "
            "notification_payload->>'workflow_id' as workflow_id, "
            "notification_payload->>'execution_time' as execution_time, "
            "notification_payload->>'cdu_id' as cdu_id, "
            "notification_payload->>'org_ids' as org_ids, "
            "notification_payload->'ticket_info'->>"
            "'ticket_creation_job_url' as ticket_creation_job_url, "
            "notification_payload->>'notification_hash' as notification_hash, "
            "notification_payload->>'deadline_minute' as deadline_minute, "
            "notification_payload->>'deadline_hour' as deadline_hour, "
            "notification_payload->>'deadline_day_of_the_month' as deadline_day_of_the_month, "
            "notification_payload->>'deadline_month' as deadline_month, "
            "notification_payload->>'deadline_day_of_week' as deadline_day_of_week, "
            "notification_payload->>'deadline_year' as deadline_year, "
            "notification_payload->>'timezone' as timezone "
            f'FROM {NOTIFICATION_HISTORY_TABLE}{limit_expression};");'
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)

    def get_notification_history_by_dataset_id(
        self, profile: str, data_adapter: Callable, dataset_id: str
    ):
        database = get_postgres_database(profile)

        query = (
            f'SELECT * FROM EXTERNAL_QUERY("{database}", '
            '"SELECT CAST(id AS VARCHAR), dataset_id, CAST(delivery_deadline AS VARCHAR), '
            "cast(notification_type as VARCHAR),"
            "CAST(created_at AS VARCHAR), CAST(modified_at AS VARCHAR), "
            f"notification_payload->>'file_frequency' as file_frequency, "
            f"notification_payload->>'v2_dataset_id' as v2_dataset_id, "
            f"notification_payload->>'delivery_mins_late' as delivery_mins_late, "
            f"notification_payload->>'most_recent_delivery_time' as most_recent_delivery_time, "
            f"notification_payload->>'workflow_id' as workflow_id, "
            f"notification_payload->>'execution_time' as execution_time, "
            f"notification_payload->>'cdu_id' as cdu_id, "
            f"notification_payload->>'org_ids' as org_ids, "
            f"notification_payload->'ticket_info'->>'ticket_creation_job_url'"
            " as ticket_creation_job_url, "
            f"notification_payload->>'notification_hash' as notification_hash, "
            f"notification_payload->>'deadline_minute' as deadline_minute, "
            f"notification_payload->>'deadline_hour' as deadline_hour, "
            f"notification_payload->>'deadline_day_of_the_month' as deadline_day_of_the_month, "
            f"notification_payload->>'deadline_month' as deadline_month, "
            f"notification_payload->>'deadline_day_of_week' as deadline_day_of_week, "
            f"notification_payload->>'deadline_year' as deadline_year, "
            f"notification_payload->>'timezone' as timezone "
            f"FROM {NOTIFICATION_HISTORY_TABLE} "
            f"WHERE dataset_id = '{dataset_id}';\");"
        )

        query_job = self.client.query(query)
        rows = query_job.result()

        return data_adapter(rows)
