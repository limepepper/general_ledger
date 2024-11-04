from datetime import date
from datetime import datetime

from rich import inspect


class StartDateDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name) or 0

    def __set__(self, instance, value):
        if not isinstance(value, date):
            raise ValueError("Start date must be a date object")
        instance.__dict__[self.name] = value


class EndDateDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, None)

    def __set__(self, obj, value):
        if isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%d")
        if not isinstance(value, date):
            raise ValueError("End date must be a date object: (%s)" % value)
        obj.__dict__[self.name] = value


class StartEndMixin:
    """
    Mixin class for start and end dates.
    start and end dates are required for most reports
    """

    strict_dates: bool = True
    start_date: date = None
    end_date = EndDateDescriptor()

    def __init__(self, *args, **kwargs):
        """
        date parsing args
        :param kwargs:
        """
        self.strict_dates = kwargs.pop("strict_dates", self.strict_dates)
        if "start_date" in kwargs:
            self.start_date = kwargs.pop("start_date")
        if "end_date" in kwargs:
            self.end_date = kwargs.pop("end_date")
        super().__init__(*args, **kwargs)
