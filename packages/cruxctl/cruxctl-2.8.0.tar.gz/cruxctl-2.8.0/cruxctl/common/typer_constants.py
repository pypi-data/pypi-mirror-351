import typer

from cruxctl.common.callbacks import validate_test_profile_only


CONTROL_PLANE_URL_OPTION = typer.Option(
    "--control-plane-url", "--cp", help="The URL of the control plane to use."
)

PROFILE_OPTION = typer.Option(
    "--profile",
    "-p",
    help="The application profile to use. Choose one of 3 profiles - dev, stg, prod."
    "This determines the backend resources accessed.",
)


PROFILE_OPTION_TEST_ONLY = typer.Option(
    "--profile",
    "-p",
    callback=validate_test_profile_only,
    help="The application profile to use. This determines the backend resources accessed.",
)


LISTING_LIMIT_OPTION = typer.Option(
    "--limit",
    "-l",
    min=-1,
    help="Limit for the number of entries to return. Use -1 for unlimited",
)

SORT_BY_OPTION = typer.Option("--sort-by", "-s", help="Sort the results by a field")
FILTERS_OPTION = typer.Option("--filters", "-f", help="Filter the results by a field")
PAGINATION_TOKEN_OPTION = typer.Option(
    "--pagination-token", "-pt", help="The token for pagination"
)
DATA_FORMAT_OPTION = typer.Option(
    "--output-format", "-o", case_sensitive=False, help="The output display format"
)

DATABASE_USER_OPTION = typer.Option("--user", "-u", help="Database username")
DATABASE_PASSWORD_OPTION = typer.Option("--password", "-pw", help="Database password")
DATABASE_HOST_OPTION = typer.Option("--host", "-h", help="Database host")
