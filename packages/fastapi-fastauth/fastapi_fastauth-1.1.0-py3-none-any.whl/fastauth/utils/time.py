from datetime import datetime, UTC, timezone


def now(tz: timezone = UTC) -> datetime:
    return datetime.now(tz)


def now_timestamp():
    return now().timestamp()


def now_int_timestamp():
    return int(now_timestamp())
