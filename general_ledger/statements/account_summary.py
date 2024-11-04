from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import rich.repr
from loguru import logger
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table

from general_ledger.django.models import Entry
from general_ledger.managers.transaction_entry import EntryQuerySet
from general_ledger.render.mixins.renderable import RenderableMixin
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.statements.mixins import StartEndMixin

"""
ths original idea here was to keep this class sufficiently general that it
could be used to summarize any set of entries, not just those from an account
and ledger. However, it is now clear that this makes things more complicated
than they need to be. The class is now used to summarize entries from an account
and probably can be fixed to work with general entries. This will be done in a
future refactor.
"""


# @rich.repr.auto
class AccountSummary(
    RenderableMixin,
    StartEndMixin,
):
    """
    represents an account view with summaries calculated
    """

    def __init__(
        self,
        entries,
        balance_interval=None,
        renderer=None,
        title=None,
        caption=None,
        currency=None,
        final_balance=False,
        group_intervals=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entries = entries
        self.balance_interval = balance_interval
        self.entries_before: EntryQuerySet = Entry.objects.none()
        self.entries_after: EntryQuerySet = Entry.objects.none()
        self.entries_between: EntryQuerySet = Entry.objects.none()
        self.entries_grouped: defaultdict[str, dict] = defaultdict(dict)
        """ this is a dictionary of entries grouped by interval """
        self.renderer = renderer
        self.title = title
        self.caption = caption
        self.currency = currency
        self.group_intervals = group_intervals or ["year"]
        """ group intervals is a list of keyword by which the entries should be grouped. by default it is ['year'] """
        self.final_balance: bool = final_balance
        """ this is a boolean flag as to whether the trailing balance should be
        appended to the suffix interval """
        self.debit_balance = Decimal("0.00")
        self.credit_balance = Decimal("0.00")
        self.debit_total = Decimal("0.00")
        """ the total of the debits in the range of the start to end"""
        self.credit_total = Decimal("0.00")
        """ the total of the credits in the range of the start to end"""

        self.balanced = False
        """ cache the status of the balance """

        self._group_by_intervals()
        self.balance_off()

    @property
    def is_empty(self):
        return self.entries is None

    def _group_by_intervals(self):
        entries = self.entries

        entries_before = entries.before(self.start_date, strict=True)
        entries_between = entries.between(self.start_date, self.end_date, strict=False)
        entries_after = entries.after(self.end_date, strict=True)
        entries_grouped = entries_between.get_grouped_entries(self.balance_interval)
        entries_grouped["prefix"]["entries"] = entries_before
        entries_grouped["suffix"]["entries"] = entries_after

        self.entries_grouped = entries_grouped
        self.entries_before = entries_before
        self.entries_after = entries_after
        self.entries_between = entries_between

    def balance_off(self):
        """
        balance the entries by working through the intervals, starting with the prefix
        and carrying the balances forward to the suffix
        """
        if not self.entries_grouped:
            return self

        self.process_interval(
            self.entries_grouped["prefix"],
            interval_key="prefix",
        )
        credit_cd = self.entries_grouped["prefix"]["credit_cd"]
        debit_cd = self.entries_grouped["prefix"]["debit_cd"]
        for interval_key in self.entries_grouped["meta"]["interval_keys"]:
            interval = self.entries_grouped[interval_key]
            self.process_interval(
                interval,
                debit_bd=credit_cd,
                credit_bd=debit_cd,
                interval_key=interval_key,
            )
            credit_cd = interval["credit_cd"]
            debit_cd = interval["debit_cd"]
        self.process_interval(
            self.entries_grouped["suffix"],
            debit_bd=credit_cd,
            credit_bd=debit_cd,
            interval_key="suffix",
        )
        suffix = self.entries_grouped["suffix"]
        self.debit_balance = (
            suffix["debit_total"] if suffix["debit_total"] else Decimal("0")
        )
        self.credit_balance = (
            suffix["credit_total"] if suffix["credit_total"] else Decimal("0")
        )
        self.debit_total = self.entries_between.debit_total()
        self.credit_total = self.entries_between.credit_total()
        self.balanced = True
        return self

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
        item["group_intervals"] = self.group_intervals
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

    def get_status(self, entry_set):
        if entry_set.is_empty():
            return self.Status.EMPTY
        if entry_set.is_balanced():
            if (
                (entry_set.debits().count() <= 1 and entry_set.debit_bd == 0)
                or (entry_set.debits().count() == 0 and entry_set.debit_bd)
            ) and (
                (entry_set.credits().count() <= 1 and entry_set.credit_bd == 0)
                or (entry_set.credits().count() == 0 and entry_set.credit_bd)
            ):
                return self.Status.ONELINE_CLOSE
            return self.Status.CLOSE
        if entry_set.is_credit_balance():
            return self.Status.CREDIT_BALANCE
        return self.Status.DEBIT_BALANCE

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.title
        # yield "caption", self.caption
        yield "currency", self.currency, "GBP"
        yield "group_intervals", self.group_intervals, ["year"]
        yield "interval_keys", (
            self.entries_grouped["meta"]["interval_keys"]
            if self.entries_grouped
            else "not-set"
        )
        yield "intervals", self.entries_grouped

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield f"[b]Account Summary:[/b] #{self.title}"
        my_table = Table("Attribute", "Value")
        my_table.add_row("name", self.currency)
        my_table.add_row("age", str(self.entries_grouped["meta"]["interval_keys"]))
        yield my_table

    def render(self):
        """custom rendering strategy for account summary"""
        if not self.renderer:
            self.renderer = RichConsoleRenderer()
        return super().render()

    class Status(Enum):
        """
        status of the entry_set in regard to what is required
        to balance it. This is used as a clue to determine how to render
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
