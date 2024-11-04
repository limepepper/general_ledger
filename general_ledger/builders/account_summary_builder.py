from typing import Optional

from general_ledger.builders.mixins import StartEndBuilderMixin
from general_ledger.managers.transaction_entry import EntryQuerySet
from general_ledger.django.models.account import Account
from general_ledger.django.models.ledger import Ledger
from general_ledger.django.models.transaction_entry import Entry
from general_ledger.statements.account_summary import AccountSummary


# @rich.repr.auto
class AccountSummaryBuilder(
    StartEndBuilderMixin,
):
    """
    This is a view over entries, grouped by interval, usually from an account and ledger.
    However, it can summarize any set of entries which is sometimes useful

    Summaries are produced by interval, and can be filtered by date range.
    this object is intended to be used to produce balanced off accounts
    representations for T-accounts and trial balances.
    """

    def __init__(self, **kwargs):
        """
        Initialize the builder
        """
        super().__init__(**kwargs)
        self.ledger: Optional[Ledger] = None
        self.account: Optional[Account] = None
        self.entry_set: Optional[EntryQuerySet] = None
        self.balance_interval = None  # which periods to calculate balances for
        self.caption = None
        self.title = None
        self.currency = None
        self.group_intervals = None
        self.final_balance = None

    def with_ledger(self, ledger):
        self.ledger = ledger
        return self

    def with_account(self, account):
        self.account = account
        return self

    def with_entry_set(self, entry_set: EntryQuerySet):
        self.entry_set = entry_set
        return self

    def with_balance_interval(self, balance_interval):
        self.balance_interval = balance_interval
        return self

    def with_details(self, title, caption, currency):
        self.title = title
        self.caption = caption
        self.currency = currency
        return self

    def with_by_group_intervals(self, group_intervals):
        self.group_intervals = group_intervals
        return self

    def with_final_balance(self, final_balance=True):
        self.final_balance = final_balance
        return self

    def build(self):
        super().build()
        if self.entry_set:
            entries = self.entry_set
        elif self.ledger and self.account:
            entries = Entry.objects.filter(
                transaction__ledger=self.ledger,
                account=self.account,
            )
        else:
            raise ValueError("Either (ledger and account) or entry_set are required")

        title = (
            self.title
            if self.title
            else (self.account.name if self.account else "placeholder")
        )
        caption = self.caption if self.caption else None
        currency = self.currency or (
            self.account.currency
            if self.account
            else (entries.first().account.currency if entries.first() else "GBP")
        )
        group_intervals = (
            self.group_intervals if self.group_intervals is not None else ["year"]
        )
        return AccountSummary(
            entries=entries,
            balance_interval=self.balance_interval,
            start_date=self.start_date,
            end_date=self.end_date,
            title=title,
            caption=caption,
            currency=currency,
            group_intervals=group_intervals,
            final_balance=self.final_balance,
        )
