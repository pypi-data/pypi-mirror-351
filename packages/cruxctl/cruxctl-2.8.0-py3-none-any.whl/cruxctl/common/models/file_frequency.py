from enum import Enum


class FileFrequency(Enum):
    """
    The frequency of the file delivery.
    """

    intraday = "intraday"
    daily = "daily"
    weekly = "weekly"
    bi_weekly = "bi-weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    semi_annual = "semi-annual"
    yearly = "yearly"
