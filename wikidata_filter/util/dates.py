import re
import time


ONE_DAY = 86400
MONTH_DAYS = [
    [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
]
YEAR_DAYS = [365, 366]


def date(dt: str, fmt='%Y-%m-%d') -> int:
    return int(time.mktime(time.strptime(dt, fmt)))


def date_ts(dt: str, fmt='%Y-%m-%d') -> int:
    return int(time.mktime(time.strptime(dt, fmt))*1000)


def ts2date(ts, fmt='%Y-%m-%d') -> str:
    return time.strftime(fmt, time.localtime(ts))


def ts2datetime(ts, fmt='%Y-%m-%d %H:%M:%S') -> str:
    if ts is not None:
        return time.strftime(fmt, time.localtime(ts))
    return ""


def current() -> int:
    return int(time.time())


def current_ts() -> int:
    return int(time.time()*1000)


def current_date(fmt='%Y-%m-%d') -> str:
    return ts2date(current(), fmt=fmt)


def current_time(fmt='%Y-%m-%d %H:%M:%S') -> str:
    return ts2datetime(current(), fmt=fmt)


def is_leap_year(year: int):
    if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
        return 1
    return 0


def month_days(year: int, month: int):
    return MONTH_DAYS[is_leap_year(year)][month]


def expand_date_range(dt: str):
    parts = re.split('[年月日\\-]+', dt, maxsplit=3)
    parts = [p for p in parts if p]
    # print(parts)
    if len(parts) == 3:
        ts = date('-'.join(parts))
        return ts, ts + ONE_DAY
    if len(parts) == 2:
        ts = date(f'{parts[0]}-{parts[1]}-01')
        days = month_days(int(parts[0]), int(parts[1]))
        return ts, ts + ONE_DAY * days
    if len(parts) == 1:
        year = parts[0]
        ts = date(f'{year}-01-01')
        return ts, ts + ONE_DAY * YEAR_DAYS[is_leap_year(int(year))]
    raise Exception("Invalid date")


def fill_date(dt: str or list):
    if isinstance(dt, str):
        return expand_date_range(dt)
    else:
        if len(dt) == 1:
            return expand_date_range(dt[0])
        else:
            return expand_date_range(dt[0])[0], expand_date_range(dt[1])[1]
