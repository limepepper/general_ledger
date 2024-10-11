from collections import defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum

from loguru import logger

from general_ledger.managers.transaction_entry import EntryQuerySet
from general_ledger.models.account import Account
from general_ledger.models.ledger import Ledger
from general_ledger.models.transaction_entry import Entry


class AccountBalancer:
    """
    this takes either an entry_set or account+ledger, and
    an interval type (year, month, week, day). it then sections
    up the entries by interval, creating balancing c/d and b/d
    elements where necessary.
    """

    def __init__(
        self,
        ledger: Ledger = None,
        account: Account = None,
        entry_set: EntryQuerySet = None,
        start_date=None,
        end_date=None,
        balance_interval: str = None,
    ):
        """

        :param ledger:
        :param account:
        :param entry_set:
        :param start_date:
        :param end_date:
        :param balance_interval:
        """

        if ledger and account:
            self.entries = Entry.objects.filter(
                transaction__ledger=ledger,
                account=account,
            )
        elif entry_set:
            self.entries = entry_set
        else:
            raise ValueError("ledger and account or entry_set are required")

        # print(pr_entry_set(self.entries))

        self.balance_interval = balance_interval

        self.grouped_entries = defaultdict(dict)

        logger.trace(f"processing {self.entries.count()} entries")

        self.start_date = start_date
        self.grouped_entries["prefix"]["entries"] = self.entries.before(
            self.start_date, strict=True
        )

        logger.trace(
            f"found pre-start-date {self.grouped_entries["prefix"]["entries"].count()} entries"
        )

        self.end_date = end_date if end_date else date.today()

        self.entries = self.entries.between(
            self.start_date,
            self.end_date,
            strict=False,
        )

        if balance_interval:
            self.grouped_entries.update(
                self.entries.get_grouped_entries(balance_interval)
            )
        else:
            self.grouped_entries["all"]["entries"] = self.entries
            self.grouped_entries["all"][
                "interval_key_dt"
            ] = self.entries.first().trans_date
            self.grouped_entries["all"]["interval_key"] = "all"
            self.grouped_entries["meta"]["interval_keys"] = ["all"]

        self.grouped_entries["suffix"]["entries"] = self.entries.after(
            self.end_date, strict=True
        )

        # process the pre-start-date entries
        self.process_interval(
            self.grouped_entries["prefix"],
            debit_bd=Decimal("0.00"),
            interval_key="prefix",
        )

        credit_cd = self.grouped_entries["prefix"]["credit_cd"]
        debit_cd = self.grouped_entries["prefix"]["debit_cd"]
        # inspect(self.grouped_entries)
        if (
            "meta" in self.grouped_entries
            and "interval_keys" in self.grouped_entries["meta"]
        ):
            for interval_key in self.grouped_entries["meta"]["interval_keys"]:
                interval = self.grouped_entries[interval_key]
                self.process_interval(
                    interval,
                    debit_bd=credit_cd,
                    credit_bd=debit_cd,
                    interval_key=interval_key,
                )
                credit_cd = interval["credit_cd"]
                debit_cd = interval["debit_cd"]
        else:
            raise ValueError("no interval keys found")

        self.process_interval(
            self.grouped_entries["suffix"],
            debit_bd=credit_cd,
            credit_bd=debit_cd,
            interval_key="suffix",
        )

        self.status = self.Status.OPEN

    def process_interval(
        self,
        item,
        debit_bd=None,
        credit_bd=None,
        interval_key=None,
    ):
        """
        process the entries for a given interval
        """
        logger.trace(f"processing interval: '{interval_key}'")
        # inspect(entries.debit_total())
        # inspect(entries.credit_total())
        entries = item["entries"]
        # inspect(entries)
        entries.set_balances_bd(
            debit_bd,
            credit_bd,
        )
        # inspect(entries)
        item["status"] = self.get_status(entries)
        # inspect(entries)
        # inspect(item)
        item["debit_bd"] = debit_bd
        item["credit_bd"] = credit_bd
        item["balance_interval"] = self.balance_interval
        if item["status"] == self.Status.EMPTY:
            item["debit_total"] = Decimal("0.00")
            item["credit_total"] = Decimal("0.00")
            item["total"] = Decimal("0.00")
            item["debit_cd"] = None
            item["credit_cd"] = None
        elif item["status"] in [self.Status.CLOSE, self.Status.ONELINE_CLOSE]:
            item["debit_total"] = entries.debit_total()
            item["credit_total"] = entries.credit_total()
            item["total"] = entries.debit_total()
            item["debit_cd"] = None
            item["credit_cd"] = None
        elif item["status"] == self.Status.CREDIT_BALANCE:
            item["debit_total"] = entries.debit_total()
            item["credit_total"] = entries.credit_total()
            item["total"] = entries.credit_total()
            item["debit_cd"] = entries.credit_balance()
            item["credit_cd"] = None
        elif item["status"] == self.Status.DEBIT_BALANCE:
            item["debit_total"] = entries.debit_total()
            item["credit_total"] = entries.credit_total()
            item["total"] = entries.debit_total()
            item["debit_cd"] = None
            item["credit_cd"] = entries.debit_balance()
        else:
            raise ValueError("unknown status")

        # inspect(item)

    def get_status(self, entry_set):
        if entry_set.is_empty():
            return self.Status.EMPTY
        if (
            entry_set.is_balanced()
            and (
                (entry_set.debits().count() == 1 and entry_set.debit_bd == 0)
                or (entry_set.debits().count() == 0 and entry_set.debit_bd)
            )
            and (
                (entry_set.credits().count() == 1 and entry_set.credit_bd == 0)
                or (entry_set.credits().count() == 0 and entry_set.credit_bd)
            )
        ):
            return self.Status.ONELINE_CLOSE
        if entry_set.is_balanced():
            return self.Status.CLOSE
        if entry_set.is_credit_balance():
            return self.Status.CREDIT_BALANCE
        return self.Status.DEBIT_BALANCE

    class Status(Enum):
        """
        status of the entry_set in regard to what is required
        to balance it. This is used to determine how to render
        the entries in the console.
        """

        OPEN = 0
        EMPTY = 1
        """
        This interval has no entries, including any balance b/d
        """
        CLOSE = 2
        """
        This interval is already balanced, needs to be closed off
        with totals
        """
        CREDIT_BALANCE = 3
        """
        This interval is not balanced on credit side, needs to be balanced
        and totals added
        """
        DEBIT_BALANCE = 4
        """
        This interval is not balanced on debit side, needs to be balanced        and totals added
        """
        ONELINE_CLOSE = 5
        """
        This interval has a single debit and a single credit, and is balanced. Indicates a one line close, i.e. no totals just underlines
        """
