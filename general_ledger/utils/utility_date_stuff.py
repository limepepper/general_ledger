import datetime
from collections import OrderedDict
from collections import namedtuple
from enum import Enum

from dateutil.relativedelta import relativedelta

EntryObject = namedtuple(
    "EntryObject",
    [
        "trans_date",
        "narrative",
        "amount",
    ],
)


class PeriodKind(str, Enum):
    """Enumeration of valid period types"""

    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"


def get_interval_key(date, group_intervals):
    key = []
    for interval in group_intervals:
        if interval == "year":
            key.append(date.year)
        elif interval == "month":
            key.append(date.year)
            key.append(date.month)
        elif interval == "week":
            key.append(date.year)
            key.append(date.isocalendar()[1])
        elif interval == "day":
            key.append(date.year)
            key.append(date.month)
            key.append(date.day)
    return tuple(OrderedDict.fromkeys(key)) if key else "none"


def last_day_of(dt, kind):
    """
    this function returns the last day of the period
    :param dt:
    :param kind:
    :return:
    """
    last_day = None
    if kind == "year":
        last_day = (dt + relativedelta(years=1)).replace(
            month=1, day=1
        ) - relativedelta(days=1)
    elif kind == "month":
        last_day = (dt + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
    elif kind == "week":
        last_day = dt + relativedelta(days=(7 - dt.isoweekday()))
    else:
        # @TODO this should throw error ii the kind is not recognized
        # but it is being used somewhere to fall through
        last_day = datetime.datetime.today() - relativedelta(days=1)
    # else:
    #     raise ValueError(f"kind: {kind} not supported")
    result = last_day if type(last_day) is datetime.date else last_day.date()
    return result


def first_day_of_next(dt, kind):
    first_day = last_day_of(dt, kind) + relativedelta(days=1)
    return first_day


def pad_around_char(date_str, char="."):
    """Pads a date string centered on the dot. convenience method for columnar dates

    Args:
      date_str: The date string to pad, in the format "day.month".

    Returns:
      The padded date string.
    """
    day, month = date_str.split(char)
    return f"{day.rjust(2)}{char}{month.ljust(2)}"
