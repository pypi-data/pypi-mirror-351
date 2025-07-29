from pathlib import Path

import platformdirs
import typer
from dotenv import set_key, load_dotenv, unset_key
from rich.console import Console

from cruxctl.command_groups.auth.auth_utilities import validate_profile, ProfileEnum
from cruxctl.common.utils.api_utils import read_config_file
import os

app = typer.Typer()
console = Console()
PROFILE_ENV_VAR = "CRUX_ACTIVE_PROFILE"


def load_active_profile_env_file():
    config_file_path = __get_active_profile_path()
    env_path = Path(config_file_path)
    if not env_path.exists():
        console.print(
            "[red]No active profile set. Defaulting to prod. "
            "Use `cruxctl profile set` command to default to a different(dev,stg) profile.[/red]"
        )
        env_path.touch()
    else:
        load_dotenv(config_file_path)


@app.command("set")
def set_current_profile(
    profile: str = typer.Argument(..., help="The profile to set - dev, stg or prod."),
):
    """
    Set the profile to use out of dev,stg or prod.
    """
    validate_profile(profile)
    config = read_config_file()
    if profile not in config:
        console.print(
            f"[red]Profile {profile} not found in config. "
            f"Please run 'cruxctl auth login -p' first.[/red]"
        )
        raise typer.Exit(code=1)
    set_active_profile_in_env(profile)
    load_active_profile_env_file()
    console.print(f"Profile set to: [green]{os.environ[PROFILE_ENV_VAR]}[/green]")


def __get_active_profile_path():
    crux_config_dir = platformdirs.user_config_dir("crux")
    return os.path.join(crux_config_dir, "active_profile.env")


def set_active_profile_in_env(profile: str):
    config_file_path = __get_active_profile_path()
    if not Path(config_file_path).exists():
        Path(config_file_path).touch()

    set_key(
        dotenv_path=config_file_path, key_to_set=PROFILE_ENV_VAR, value_to_set=profile
    )


def unset_active_profile_in_env():
    config_file_path = __get_active_profile_path()
    if not Path(config_file_path).exists():
        Path(config_file_path).touch()

    unset_key(dotenv_path=config_file_path, key_to_unset=PROFILE_ENV_VAR)


@app.command("get")
def get_current_profile():
    """
    Get the current profile.
    """
    load_active_profile_env_file()
    current_profile = os.getenv(PROFILE_ENV_VAR)
    if not current_profile:
        console.print(
            "[red]No profile set. Defaulting to prod. "
            "Use `cruxctl profile set` command to default to a different (dev,stg) profile.[/red]"
        )
        current_profile = ProfileEnum.PROD.value

    config = read_config_file()
    if current_profile not in config:
        console.print(
            f"[red]Credentials for Profile {current_profile} not found in config. "
            f"Please run 'cruxctl auth login --profile {current_profile}' first.[/red]"
        )
        raise typer.Exit(code=1)

    set_active_profile_in_env(current_profile)
    console.print(f"Current profile is: [green]{current_profile}[/green]")
    return current_profile
