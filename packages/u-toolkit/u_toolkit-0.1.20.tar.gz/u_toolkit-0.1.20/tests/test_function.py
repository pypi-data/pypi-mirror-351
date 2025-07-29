from u_toolkit import function


def test_get_name():
    def fn(): ...

    assert function.get_name(fn) == "fn"
    assert function.get_name(lambda: 1) == "<lambda>"


def test_add_document():
    def fn(): ...

    assert fn.__doc__ is None

    function.add_document(fn, "lalala")

    assert fn.__doc__ == "lalala"

    def fn2():
        """2333"""

    assert fn2.__doc__ == "2333"

    function.add_document(fn2, "lalala")
    assert fn2.__doc__ == "2333\n\nlalala"
