# pragma: no cover

from mixpanel import Mixpanel
import platform
import requests
from cruxctl.common.utils.api_utils import get_user_info_by_token, get_plan_types


def track_mixpanel_event(
    event_name: str, properties: dict, api_token: str, profile: str, mixpanel_token: str
) -> None:
    """
    Tracks an event in Mixpanel.
    :param event_name: The name of the event to track.
    :param properties: Properties to include with the event.
    :param api_token: The API token retrieved during the initial cruxctl command.
    :param profile: The profile being used (e.g., local, dev, staging, prod).
    :param mixpanel_token: The Mixpanel token for authentication.
    """
    try:
        user_profile = get_user_info_by_token(api_token, profile)
        if "email" not in user_profile:
            return
        user_email = user_profile["email"]
        plan_types = get_plan_types(user_profile["orgId"], api_token, profile)
        properties["Plan Type"] = plan_types
        properties["Organization"] = user_profile["orgId"]
        properties["User ID"] = user_profile["email"]

        mp = Mixpanel(mixpanel_token)

        # Add OS information
        if platform.system() == "Darwin":
            properties["$os"] = "Mac OS X"
        else:
            properties["$os"] = platform.system()

        # Add location information
        response = requests.get("https://ipinfo.io", timeout=5)
        if response.status_code == 200:
            location_data = response.json()
            properties["$city"] = location_data.get("city", "Unknown")
            properties["mp_country_code"] = location_data.get("country", "Unknown")

        # Track the event
        mp.track(user_email, event_name, properties)
    except Exception:
        pass
