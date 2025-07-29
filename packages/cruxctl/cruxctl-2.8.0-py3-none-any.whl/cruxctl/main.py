import typer

from cruxctl.command_groups.auth import auth
from cruxctl.command_groups.dataset import dataset
from cruxctl.command_groups.dataset_health import dataset_health
from cruxctl.command_groups.deadlines import deadlines
from cruxctl.command_groups.profile import profile

app = typer.Typer(rich_markup_mode="rich")
app.add_typer(
    deadlines.app,
    name="deadlines",
    help="Manage dataset delivery deadlines, "
    "Do not forget to set CRUX_API_TOKEN environment variable "
    "before running the commands.",
)
app.add_typer(
    dataset_health.app, name="dataset-health", help="Query dataset health info"
)
app.add_typer(
    dataset.app, name="dataset", help="Routines related to handling datasets."
)
app.add_typer(auth.app, name="auth", help="Authenticate with the Crux Control Plane.")
app.add_typer(
    profile.app, name="profile", help="Set the profile to use out of dev,stg or prod."
)

__version__ = "2.8.0"
# This file needs the version too.
auth.set_global_version(__version__)


@app.command(help="Gets the CLI version")
def version():
    print(f"CruxCtl Version: {__version__}")


if __name__ == "__main__":
    app()
