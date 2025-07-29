from enum import Enum


class SchemaClass(Enum):
    OBSERVED = "OBSERVED"
    DECLARED = "DECLARED"
    CONFIGURED = "CONFIGURED"


CURATION_EVENT_TYPE = "com.crux.cp.dataset.curation.success.v1"
