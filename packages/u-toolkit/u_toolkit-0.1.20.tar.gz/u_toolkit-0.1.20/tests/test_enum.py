from u_toolkit import enum


def test_name_enum():
    class _Enum(enum.NameEnum):
        A = enum.auto()
        Ab = enum.auto()
        AbC = enum.auto()
        ABCD = enum.auto()
        ABCD_E = enum.auto()
        aa = enum.auto()
        a_a = enum.auto()
        a2 = enum.auto()
        Bb = enum.auto()
        c_ = enum.auto()

    assert _Enum.A == "A"
    assert _Enum.Ab == "Ab"
    assert _Enum.AbC == "AbC"
    assert _Enum.ABCD == "ABCD"
    assert _Enum.ABCD_E == "ABCD_E"
    assert _Enum.aa == "aa"
    assert _Enum.a_a == "a_a"
    assert _Enum.a2 == "a2"
    assert _Enum.Bb == "Bb"
    assert _Enum.c_ == "c_"


def test_pascal_enum():
    class _Enum(enum.PascalEnum):
        A = enum.auto()
        Ab = enum.auto()
        AbC = enum.auto()
        ABCD = enum.auto()
        ABCD_E = enum.auto()
        aa = enum.auto()
        a_a = enum.auto()
        a2 = enum.auto()
        Bb = enum.auto()
        c_ = enum.auto()

    assert _Enum.A == "A"
    assert _Enum.Ab == "Ab"
    assert _Enum.AbC == "Abc"
    assert _Enum.ABCD == "ABCD"
    assert _Enum.ABCD_E == "ABCD_E"
    assert _Enum.aa == "Aa"
    assert _Enum.a_a == "AA"
    assert _Enum.a2 == "A2"
    assert _Enum.Bb == "Bb"
    assert _Enum.c_ == "C_"


def test_camel_enum():
    class _Enum(enum.CamelEnum):
        A = enum.auto()
        Ab = enum.auto()
        AbC = enum.auto()
        ABCD = enum.auto()
        ABCD_E = enum.auto()
        aa = enum.auto()
        a_a = enum.auto()
        a2 = enum.auto()
        Bb = enum.auto()
        c_ = enum.auto()

    assert _Enum.A == "A"
    assert _Enum.Ab == "ab"
    assert _Enum.AbC == "abc"
    assert _Enum.ABCD == "ABCD"
    assert _Enum.ABCD_E == "ABCD_E"
    assert _Enum.aa == "aa"
    assert _Enum.a_a == "aA"
    assert _Enum.a2 == "a2"
    assert _Enum.Bb == "bb"
    assert _Enum.c_ == "c_"


def test_snake_enum():
    class _Enum(enum.SnakeEnum):
        A = enum.auto()
        Ab = enum.auto()
        AbC = enum.auto()
        ABCD = enum.auto()
        ABCD_E = enum.auto()
        aa = enum.auto()
        a_a = enum.auto()
        a2 = enum.auto()
        aa3 = enum.auto()
        Bb = enum.auto()
        c_ = enum.auto()

    assert _Enum.A == "A"
    assert _Enum.Ab == "ab"
    assert _Enum.AbC == "ab_c"
    assert _Enum.ABCD == "ABCD"
    assert _Enum.ABCD_E == "ABCD_E"
    assert _Enum.aa == "aa"
    assert _Enum.a_a == "a_a"
    assert _Enum.a2 == "a_2"
    assert _Enum.aa3 == "aa_3"
    assert _Enum.Bb == "bb"
    assert _Enum.c_ == "c_"


def test_title_enum():
    class _Enum(enum.TitleEnum):
        A = enum.auto()
        Ab = enum.auto()
        AbC = enum.auto()
        ABCD = enum.auto()
        ABCD_E = enum.auto()
        aa = enum.auto()
        a_a = enum.auto()
        a2 = enum.auto()
        aa3 = enum.auto()
        Bb = enum.auto()
        c_ = enum.auto()

    assert _Enum.A == "A"
    assert _Enum.Ab == "Ab"
    assert _Enum.AbC == "Abc"
    assert _Enum.ABCD == "Abcd"
    assert _Enum.ABCD_E == "Abcd E"
    assert _Enum.aa == "Aa"
    assert _Enum.a_a == "A A"
    assert _Enum.a2 == "A2"
    assert _Enum.aa3 == "Aa3"
    assert _Enum.Bb == "Bb"
    assert _Enum.c_ == "C"
