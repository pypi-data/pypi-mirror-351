import base64
import json
import os
from typing import Dict, Any
import yaml

import requests
import platformdirs
from requests import HTTPError, Response
from rich.console import Console

from cruxctl.common.constants import default_profile

MAX_PAGE_SIZE: int = 1000


def read_config_file() -> Dict[str, Any]:
    # Check for platform dirs crux config.yaml
    config_file_path = get_config_file_path()
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            existing_file = yaml.safe_load(file)
            return existing_file if existing_file else {}
    else:
        return {}


def get_config_file_path() -> str:
    crux_config_dir = platformdirs.user_config_dir("crux")
    return os.path.join(crux_config_dir, "config.yaml")


def get_api_base_url(profile: str) -> str:
    """
    Get the base URL for the control plane REST calls.
    """
    env_url = os.environ.get("CONTROL_PLANE_URL")
    if env_url:
        return env_url

    config = read_config_file()

    if "CONTROL_PLANE_URL" in config.get(profile, {}):
        return config[profile]["CONTROL_PLANE_URL"]

    return "https://api.cruxinformatics.com"


def get_control_plane_url(profile: str) -> str:
    """
    Get the URL for the control plane REST calls.
    """
    return f"{get_api_base_url(profile)}/ops/control-plane"


def get_url_based_on_profile(
    profile: str, version: str = "v2", swap_ops_version: bool = False
) -> str:
    ops = "ops"
    if swap_ops_version:
        # The Crux API CHANGED THE ORDER OF OPS AND THE VERSION in the new version of the API.
        # For example, we have the old call /v4/ops/data-products and the new call
        # /ops/v4/data-products/maps. I talked to Naveen and that's the way it is.
        ops = version
        version = "ops"
    return f"{get_api_base_url(profile)}/{version}/{ops}"


def get_document_url(
    profile: str, version: str = "v2", swap_ops_version: bool = False
) -> str:
    """
    Get the URL for document upload
    """
    return f"{get_url_based_on_profile(profile, version, swap_ops_version)}/documents?active=true&"


def get_data_product_url(
    profile: str, version: str = "v2", swap_ops_version: bool = False
) -> str:
    """
    Get the URL for document upload
    """
    return (
        f"{get_url_based_on_profile(profile, version, swap_ops_version)}/data-products"
    )


def get_api_headers(token: str) -> dict[str, str]:
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    return headers


def set_api_token(console: Console, profile) -> str:
    env_token = os.environ.get("CRUX_API_TOKEN", None)

    if not env_token:
        config = read_config_file()

        if config != {}:
            profile = config.get(profile, {})
            env_token = profile.get("CRUX_API_TOKEN", None)
            if not env_token:
                raise Exception(
                    "CRUX_API_TOKEN not found for profile. Please run 'cruxctl auth login' first."
                )
            else:
                return env_token
        else:
            raise Exception(
                "No config found for profile. Please run 'cruxctl auth login' first."
            )


def raise_for_status(response: Response):
    """
    Checks the HTTP response for an error status and raises an HTTPError if one occurred.

    Args:
        response (Response): The HTTP response to check.

    Raises:
        HTTPError: If the response contains an error status (400-599).
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


def get_auth_payload(auth: str) -> Dict[str, Any]:
    """
    Get auth token payload
    :param auth: auth token
    """
    auth and isinstance(auth, str)

    token = auth.replace("Bearer ", "")
    auth_token_components = token.split(".")
    # If you look at an auth token, it is split in 3 parts via a dot.
    # The first part is the header, the second part is the payload,
    # and the third part is the signature. We ignore the header and signature.
    if len(auth_token_components) != 3:
        raise Exception("Invalid token")
    payload_str = base64.urlsafe_b64decode(auth_token_components[1] + "==").decode()
    # Convert from string to dict.
    return json.loads(payload_str)


def get_user_info_by_token(
    access_token: str, profile: str = default_profile
) -> Dict[str, Any]:
    """
    Get user info by email from identity service
    :param email: email of the user to look up.
    :param access_token: OAuth access token.
    """
    access_token and isinstance(access_token, str)

    rest_url = f"{get_url_based_on_profile(profile)}/user/profile"
    headers = {
        "authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(rest_url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_plan_types(
    org_id: str, access_token: str, profile: str = default_profile
) -> str:
    """
    Gets the active plan types for an org.
    :param str org_id: The org ID to look up for the plan types.
    :param str access_token: The token for authenticating to the Crux API.
    :param str profile: The environment we are running in (dev, stg, prod).
    :return: A string listing the plan types that are active with a space between them.
    """
    assert org_id and isinstance(org_id, str)
    assert access_token and isinstance(access_token, str)
    assert profile and isinstance(profile, str)

    rest_url = f"{get_url_based_on_profile(profile)}/orgs/{org_id}"
    headers = {
        "authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(rest_url, headers=headers)
    response.raise_for_status()
    data_dict = response.json()
    plan_types = []
    if "attr" in data_dict and "subscriptions" in data_dict["attr"]:
        subscriptions = data_dict["attr"]["subscriptions"]
        if (
            "EDP" in subscriptions
            and "status" in subscriptions["EDP"]
            and subscriptions["EDP"]["status"] == "ACTIVE"
        ):
            plan_types.append("Self-Service")
        if (
            "FORGE" in subscriptions
            and "status" in subscriptions["FORGE"]
            and subscriptions["FORGE"]["status"] == "ACTIVE"
        ):
            plan_types.append("Forge")
    return " ".join(plan_types)
