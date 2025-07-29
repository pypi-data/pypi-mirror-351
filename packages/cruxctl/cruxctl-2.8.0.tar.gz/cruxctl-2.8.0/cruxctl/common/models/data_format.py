from enum import Enum


class DataFormat(str, Enum):
    """
    Supported output data formats for the CLI
    """

    json = "json"
    table = "table"
    tree = "tree"
