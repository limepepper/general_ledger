import itertools
from datetime import datetime, date
from decimal import Decimal

from rich import inspect


class AccountTAccount:
    def __init__(
        self,
        name,
        reference,
        debit_entries=None,
        credit_entries=None,
    ):
        self.name = name
        self.reference = reference
        self.debit_entries = debit_entries if debit_entries is not None else []
        self.credit_entries = credit_entries if credit_entries is not None else []

    def report(self):
        output = ""
        output += self.header()
        output += self.report_rows()
        return output

    def header(self):
        output = ""
        output += f"{self.name.center(81)}\n"
        output += "-" * 81 + "\n"
        return output

    def report_rows(self):
        zipped = list(
            itertools.zip_longest(
                self.debit_entries,
                self.credit_entries,
                fillvalue=None,
            )
        )
        inspect(zipped)
        out = ""
        for foo in zipped:
            out += self.report_row(foo)
        return out

    def report_row(self, e):
        output = ""
        output += f"{self.col_item(e[0])}|{self.col_item(e[1])}\n"
        return output

    def col_item(self, item):
        datex = item.date if item and hasattr(item, "date") else ""
        if isinstance(datex, date):
            datex = datex.strftime("%Y-%m-%d")
        narrative = item.narrative if item else ""
        if hasattr(item, "amount"):
            amount = (
                f"{item.amount : >10.2f}"
                if isinstance(item.amount, Decimal)
                else f"{item.amount : >10}"
            )
        else:
            amount = ""
        return f" {datex: <8} {narrative: <19} {amount} "
