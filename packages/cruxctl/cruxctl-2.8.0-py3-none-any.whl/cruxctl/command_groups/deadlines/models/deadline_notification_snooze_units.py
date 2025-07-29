from enum import Enum


class DeadlineNotificationSnoozeUnits(str, Enum):
    """
    Supported deadline notification snoozing units
    """

    hours = "hours"
    days = "days"
