from typing import Annotated, get_origin


def is_annotated(target):
    """判断值是否是 `typing.Annotated`"""

    return get_origin(target) is Annotated
