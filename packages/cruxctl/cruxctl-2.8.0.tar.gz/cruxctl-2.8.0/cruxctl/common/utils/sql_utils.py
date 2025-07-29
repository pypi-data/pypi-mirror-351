NO_SELECT_LIMIT_VALUE = -1


def get_limit_expression(limit: int) -> str:
    return "" if limit == NO_SELECT_LIMIT_VALUE else f" LIMIT {limit}"
