from datetime import date
from datetime import datetime

from loguru import logger

from general_ledger.statements.mixins import StartEndMixin


class StartEndBuilderMixin(StartEndMixin):
    """
    Mixin class for building start and end dates.
    start and end dates are required for most reports
    """

    def with_start_date(self, start_date):
        if isinstance(start_date, date):
            self.start_date = start_date
        elif isinstance(start_date, str):
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            logger.warning("Invalid start date: %s", start_date)
        return self

    def with_end_date(self, dt):
        if isinstance(dt, date):
            self.end_date = dt
        elif isinstance(dt, datetime):
            self.end_date = dt.date()
        elif isinstance(dt, str):
            self.end_date = datetime.strptime(dt, "%Y-%m-%d").date()

        return self

    def with_date_range(self, start_date, end_date):
        self.with_start_date(start_date)
        self.with_end_date(end_date)
        return self

    def build(self):
        if self.strict_dates and not self.start_date:
            raise ValueError("start date is required")
        if not self.strict_dates and not self.start_date:
            self.start_date = date(1970, 1, 1)
        if self.strict_dates and not self.end_date:
            raise ValueError("end date is required (builder)")
        if not self.strict_dates and not self.end_date:
            self.end_date = date.today()
