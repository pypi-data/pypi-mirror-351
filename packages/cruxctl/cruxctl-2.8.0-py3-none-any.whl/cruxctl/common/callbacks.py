from datetime import datetime

import typer

from cruxctl.common.models.application_profile import ApplicationProfile


def datetime_to_date(ctx: typer.Context, datetime_value: datetime):
    if ctx.resilient_parsing:
        return

    return datetime_value.date() if datetime_value else None


def validate_test_profile_only(ctx: typer.Context, profile: ApplicationProfile):
    if ctx.resilient_parsing:
        return

    if profile != ApplicationProfile.local:
        raise typer.BadParameter(
            f"Only the test profile is allowed. Invalid profile: {profile}"
        )
