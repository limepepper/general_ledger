from datetime import date
from datetime import datetime

from general_ledger.utils.income_statement import IncomeStatement


class IncomeStatementBuilder:
    def __init__(
        self,
        *,
        ledger,
        start_date,
        end_date,
        **kwargs,
    ):
        self.ledger = ledger
        if not self.ledger:
            raise ValueError("Ledger is required")
        self.book = self.ledger.book

        if not start_date:
            raise ValueError("start date is required")
        if isinstance(start_date, date):
            self.start_date = start_date
        else:
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        if not end_date:
            raise ValueError("end date is required (builder)")
        if isinstance(end_date, date):
            self.end_date = end_date
        else:
            self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        print(self.end_date)

    def build(self):
        print(f"building income statement from {self.start_date} to {self.end_date}")
        return IncomeStatement(
            self.ledger,
            self.start_date,
            self.end_date,
        )
