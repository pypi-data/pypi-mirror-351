from datetime import UTC, datetime


def to_utc(dt: datetime, /) -> datetime:
    """转成 UTC 时间

    :param dt: 时间
    :return: UTC 时间
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_naive(dt: datetime, /) -> datetime:
    """去除时区标识

    :param v: 时间
    :return: 不带时区标识的时间
    """
    return dt.replace(tzinfo=None)


def to_utc_naive(dt: datetime, /) -> datetime:
    """将时间转换成不带时区标识的 UTC 时间

    :param v: 时间
    :return: 不带时区标识的 UTC 时间
    """
    return to_naive(to_utc(dt))
