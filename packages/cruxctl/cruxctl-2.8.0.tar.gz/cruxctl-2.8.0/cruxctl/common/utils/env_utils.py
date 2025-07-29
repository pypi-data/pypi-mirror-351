import os
from typing import Optional

from cruxctl.common.utils.gcp_secrets_manager import get_secret_value


def set_openai_token(console):
    token = os.environ.get("OPENAI_API_KEY", None)
    if not token:
        secret_proj = "crux-data-science"
        secret_key = "OPENAI_API_KEY"
        console.rule("[bold red]Remove before public release", style="red")
        console.print(f"Fetching GCP secret: {secret_proj}/{secret_key}")
        console.rule(style="red")
        token = get_secret_value(secret_proj, secret_key)
        os.environ["OPENAI_API_KEY"] = token
    return token


def get_mixpanel_token() -> Optional[str]:
    """
    Get the Mixpanel token from the environment. If it can't find it, it returns None.
    :return: The Mixpanel token from the environment or empty string if it doesn't exist.
    """
    # The default IS NOT something that has to be protected by a password. It is simply
    # an identifier of which Mixpanel board to post to.
    return os.getenv("MIXPANEL_TOKEN", default="3a3176998429147c906cd53d35b88282")
