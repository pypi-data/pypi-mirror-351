import typer
from enum import Enum


# Step 1: Define an Enum for profiles
class ProfileEnum(str, Enum):
    DEV = "dev"
    STAGING = "stg"
    PROD = "prod"


# Step 3: Function to validate a profile
def validate_profile(profile: str) -> ProfileEnum:
    try:
        return ProfileEnum(profile)
    except ValueError:
        raise typer.BadParameter("Profile must be one of 'dev', 'stg', or 'prod'.")
