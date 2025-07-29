from cruxctl.common.models.application_profile import ApplicationProfile


_POSTGRES_DATABASE_LOOKUP = {
    ApplicationProfile.local: (
        "projects/crux-staging/locations/us/"
        "connections/crux-stg-pgdb-1-gusc1-read-replica"
    ),
    ApplicationProfile.staging: (
        "projects/crux-staging/locations/us/"
        "connections/crux-stg-pgdb-1-gusc1-read-replica"
    ),
    ApplicationProfile.prod: "crux-199318.us.crux-199318_us_crux-prod-pgdb-1-gusc1-replica-1",
}


_PROCESSING_HEALTH_TABLE_LOOKUP = {
    ApplicationProfile.local: "delivery_recon.test_dataset_processing_health_history",
    ApplicationProfile.staging: "delivery_recon.dataset_processing_health_history",
    ApplicationProfile.prod: "delivery_recon.dataset_processing_health_history",
}


_DISPATCH_HEALTH_TABLE_LOOKUP = {
    ApplicationProfile.local: "delivery_recon.test_dataset_dispatch_health_history",
    ApplicationProfile.staging: "delivery_recon.dataset_dispatch_health_history",
    ApplicationProfile.prod: "delivery_recon.dataset_dispatch_health_history",
}

_AGGREGATED_BY_DATASET_STATUS_VIEW_LOOKUP = {
    ApplicationProfile.local: "delivery_recon.test_aggregated_by_dataset_status_view",
    ApplicationProfile.staging: "delivery_recon.aggregated_by_dataset_status_view",
    ApplicationProfile.prod: "delivery_recon.aggregated_by_dataset_status_view",
}

_AGGREGATED_BY_SUBSCRIBER_STATUS_VIEW_LOOKUP = {
    ApplicationProfile.local: "delivery_recon.test_aggregated_dataset_by_subscriber_status_view",
    ApplicationProfile.staging: "delivery_recon.aggregated_dataset_by_subscriber_status_view",
    ApplicationProfile.prod: "delivery_recon.aggregated_dataset_by_subscriber_status_view",
}


def get_postgres_database(profile: ApplicationProfile) -> str:
    if profile not in _POSTGRES_DATABASE_LOOKUP:
        raise ValueError(f"Invalid profile: {profile}")

    return _POSTGRES_DATABASE_LOOKUP[profile]


def get_processing_health_table(profile: ApplicationProfile) -> str:
    if profile not in _PROCESSING_HEALTH_TABLE_LOOKUP:
        raise ValueError(f"Invalid profile: {profile}")

    return _PROCESSING_HEALTH_TABLE_LOOKUP[profile]


def get_dispatch_health_table(profile: ApplicationProfile) -> str:
    if profile not in _DISPATCH_HEALTH_TABLE_LOOKUP:
        raise ValueError(f"Invalid profile: {profile}")

    return _DISPATCH_HEALTH_TABLE_LOOKUP[profile]


def get_aggregated_by_dataset_status_view(profile: ApplicationProfile) -> str:
    if profile not in _AGGREGATED_BY_DATASET_STATUS_VIEW_LOOKUP:
        raise ValueError(f"Invalid profile: {profile}")

    return _AGGREGATED_BY_DATASET_STATUS_VIEW_LOOKUP[profile]


def get_aggregated_by_subscriber_status_view(profile: ApplicationProfile) -> str:
    if profile not in _AGGREGATED_BY_SUBSCRIBER_STATUS_VIEW_LOOKUP:
        raise ValueError(f"Invalid profile: {profile}")

    return _AGGREGATED_BY_SUBSCRIBER_STATUS_VIEW_LOOKUP[profile]
