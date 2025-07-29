from enum import Enum


class ApplicationProfile(str, Enum):
    """
    The command profile to determine which backend environment to use.
    """

    local = "local"
    dev = "dev"
    staging = "staging"
    prod = "prod"
