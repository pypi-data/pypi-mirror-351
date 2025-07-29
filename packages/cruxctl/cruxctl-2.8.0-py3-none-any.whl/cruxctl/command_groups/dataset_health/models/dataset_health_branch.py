from dataclasses import dataclass
from datetime import datetime


@dataclass
class DatasetHealthBranch:
    subscriber_id: str
    dataset_id: str
    aggregated_status: str
    delivery_deadline: datetime
    processing_status: str
    dispatch_statuses: list[str]
    subscription_ids: list[str]
