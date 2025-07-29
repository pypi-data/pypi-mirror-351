from sqlalchemy import text

from cruxctl.command_groups.dataset_health.models.dataset_health_profile import (
    get_processing_health_table,
    get_dispatch_health_table,
)
from cruxctl.common.models.application_profile import ApplicationProfile
from cruxctl.common.utils.database_utils import create_pg_database_session

AGGREGATED_BY_DATASET_HEALTH_VIEW = "delivery_recon.aggregated_by_dataset_status_view"
AGGREGATED_BY_SUBSCRIBER_HEALTH_VIEW = (
    "delivery_recon.aggregated_dataset_by_subscriber_status_view"
)
NOTIFICATION_HISTORY_TABLE = "delivery_recon.dataset_notification_history"


class PostgresDatasetHealthRepo:
    def __init__(self, user: str, password: str, host: str, database: str, port: int):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.port = port

    def delete_all_processing_health(self):
        table = get_processing_health_table(ApplicationProfile.local)
        self._truncate_table(table)

    def delete_all_dispatch_health(self):
        table = get_dispatch_health_table(ApplicationProfile.local)
        self._truncate_table(table)

    def _truncate_table(self, table: str):
        with create_pg_database_session(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database,
            port=self.port,
        ) as session:
            session.execute(text(f"TRUNCATE TABLE {table}"))
            session.commit()
