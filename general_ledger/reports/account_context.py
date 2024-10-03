import itertools
import logging
import pprint
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.db.models import CharField
from django.db.models import Q
from django.db.models.functions import Cast
from forex_python.converter import CurrencyCodes

from general_ledger.models.account import Account
from general_ledger.models.direction import Direction
from general_ledger.models.transaction_entry import Entry


class AccountContext:
    """
    to produce a T-account style report for an account
    need to generate some list of entries aggregated by years, months
    etc
    """

    logger = logging.getLogger(__name__)

    currency_codes = CurrencyCodes()

    def __init__(self, account: Account):
        self.account = account

        # this is getting all the entris associated with the account
        # however it should be taking a queryset of transactions/entries
        # and then filtering them by account or something like that
        self.entries = account.entry_set.all()

        self.debits = self.entries.filter(tx_type=Direction.DEBIT)
        self.creditz = self.entries.filter(tx_type=Direction.CREDIT)

        self.debit_balance = self.get_debit_balance()
        self.credit_balance = self.get_credit_balance()

        self.years = sorted(
            list(set([entry.trans_date.year for entry in self.entries]))
        )

        self.debit_years = list(set([entry.trans_date.year for entry in self.debits]))

        self.credits_years = list(
            set([entry.trans_date.year for entry in self.creditz])
        )

        sorted_dict = defaultdict(list)

        for entry in self.entries:
            key = entry.trans_date.strftime("%Y-%m")
            sorted_dict[key].append(entry)

        self.logger.debug(
            f"years: {self.years} debit_years: {self.debit_years} credits_years: {self.credits_years}\n"
            f" sorted_dict: {pprint.pformat(sorted_dict)}\n"
        )

    class EntryRow:
        """
        stupid class to hold either an entry or a closing entry
        """

        def __init__(self, date: datetime, narrative: str, amount: Decimal):
            self.date = date
            self.narrative = narrative
            self.amount = amount

    def get_debit_balance(self):
        return sum([entry.amount for entry in self.debits])

    def get_credit_balance(self):
        return sum([entry.amount for entry in self.creditz])

    def get_balance(self):
        return abs(self.credit_balance - self.debit_balance)

    def is_credit_balance(self):
        return self.credit_balance > self.debit_balance

    def is_debit_balance(self):
        return self.debit_balance > self.credit_balance

    def get_context_report(self):
        output = ""
        output += f"{self.account.name.center(81)}\n"
        output += "-" * 81 + "\n"
        for year in self.years:
            cur = self.currency_codes.get_symbol(self.account.currency).center(10)
            output += f" {year: <28} {cur: >10}"
            output += "|"
            output += f" {year: <28} {cur.center(10): >10}\n"

        return output

    def get_year_row(self):
        pass

    def get_account_console_summary(self):
        """
        print the header and loop the entries
        """
        output = ""
        output += f"{self.account.name.center(81)}\n"
        output += "-" * 81 + "\n"
        # output += f"balance: {self.account.balance}\n"
        # output += "\n"
        output += self.get_report_rows()
        output += "\n"
        output += "\n"
        return output

    def get_report_rows(self):
        output = ""
        output += self.get_account_console_entry_summary(self.entries, self.account)
        return output

    def get_account_console_entry_summary(self, entryset, account):

        years = sorted(list(set([entry.trans_date.year for entry in entryset])))
        debits = entryset.filter(tx_type=Direction.DEBIT)
        creditz = entryset.filter(tx_type=Direction.CREDIT)

        output = ""
        for year in years:
            debits1 = [
                self.EntryRow(
                    e.transaction.trans_date.strftime("%b %e"),
                    self.get_counter_entry(e),
                    e.amount,
                )
                for e in entryset.filter(
                    tx_type=Direction.DEBIT,
                    transaction__trans_date__year=year,
                )
            ]
            creditz1 = [
                self.EntryRow(
                    e.transaction.trans_date.strftime("%b %e"),
                    self.get_counter_entry(e),
                    e.amount,
                )
                for e in entryset.filter(
                    tx_type=Direction.CREDIT,
                    transaction__trans_date__year=year,
                )
            ]

            if self.is_debit_balance():
                creditz1.append(
                    self.EntryRow(
                        date=datetime.now().strftime("%b %e"),
                        narrative="Balance c/d",
                        amount=self.get_balance(),
                    )
                )
            else:
                debits1.append(
                    self.EntryRow(
                        date=datetime.now().strftime("%b %e"),
                        narrative="Balance c/d",
                        amount=self.get_balance(),
                    )
                )

            zipped = list(itertools.zip_longest(debits1, creditz1, fillvalue=None))

            if len(zipped) == 0:
                continue
            # self.logger.info(f"year: {year} account: {account}")
            output += self.get_year_header_row(year, account, debits1, creditz1)

            # print(len(zipped))
            # print(f"type of zipped: {type(zipped)}")
            for e in zipped:
                # print(f"type of e: {type(e)}")
                # print(f"type of e[0]: {type(e[0])}")
                output += f"{self.get_entry_row(e[0])}|{self.get_entry_row(e[1])}\n"

            # output += self.get_totals_row(account)

        return output

    def get_year_header_row(self, year, account, debits1, creditz1) -> str:
        output = ""
        if len(debits1) and len(creditz1):
            output += f" {year: <31} {account.currency_symbol.center(6)} | {year: <28} {account.currency_symbol.center(10): >10}\n"
        elif len(debits1):
            output += (
                f" {year: <31} {account.currency_symbol.center(6): >6} | {' '*39}\n"
            )
        elif len(creditz1):
            output += (
                f" {' '*38} | {year: <28} {account.currency_symbol.center(10): >10}\n"
            )
        return output

    def get_entry_row(self, entry: EntryRow):
        # print(type(entry))
        output = ""
        if entry:
            # print(f"entry.date is {entry.date}")
            output += f" {entry.date: <8}{entry.narrative: <19} {entry.amount : >10} "
        else:
            output += f" {' '*38} "
        return output

    def get_totals_row(self, account):
        output = ""
        output += f" {'------'.rjust(38)} | {'-------'.rjust(38)}\n"
        output += f" {str(self.get_debit_balance()).rjust(38)} | {str(self.get_credit_balance()).rjust(38)}\n"
        output += f" {'======'.rjust(38)} | {'======='.rjust(38)}\n"
        return output

    def get_counter_entry(self, entry: Entry):
        """
        if the entry has a single opposite, return it
        """

        ety = entry.transaction.entry_set.filter(
            ~Q(id=entry.id) & Q(tx_type=Direction(entry.tx_type).opposite())
        ).values_list("account__name", flat=True)

        accounts = ", ".join(ety)
        return accounts if accounts else None
