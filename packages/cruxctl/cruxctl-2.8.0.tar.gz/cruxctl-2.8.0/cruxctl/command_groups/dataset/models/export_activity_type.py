from enum import Enum


class ExportActivityType(str, Enum):
    SUCCESS = "SUCCESS"
    OBSOLETE = "OBSOLETE"
