from typing import Annotated

from u_toolkit import helpers


def test_is_annotated():
    assert helpers.is_annotated(type) is False
    assert helpers.is_annotated(int) is False
    assert helpers.is_annotated(object()) is False
    assert helpers.is_annotated(Annotated) is False
    assert helpers.is_annotated(Annotated[int, 1]) is True
    assert helpers.is_annotated(Annotated[int, type]) is True
    assert helpers.is_annotated(Annotated[int, object()]) is True
