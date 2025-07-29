from enum import Enum


class DatasetExpectedDeliveryDeadlineColumn(Enum):
    dataset_id = "dataset_id"
    deadline_minute = "deadline_minute"
    deadline_hour = "deadline_hour"
    deadline_day_of_the_month = "deadline_day_of_the_month"
    deadline_month = "deadline_month"
    deadline_day_of_week = "deadline_day_of_week"
    deadline_year = "deadline_year"
    timezone = "timezone"


class DatasetExpectedDeliveryDeadlineColumnCamelCase(Enum):
    dataset_id = "datasetId"
    deadline_minute = "deadlineMinute"
    deadline_hour = "deadlineHour"
    deadline_day_of_the_month = "deadlineDayOfTheMonth"
    deadline_month = "deadlineMonth"
    deadline_day_of_week = "deadlineDayOfWeek"
    deadline_year = "deadlineYear"
    timezone = "timezone"
    file_frequency = "fileFrequency"
    is_active = "isActive"
    is_excluded = "isExcluded"


class DatasetExpectedDeliveryDeadlineJoinedColumn(Enum):
    workflow_id = "workflow_id"
