from dataclasses import dataclass, field
from django.db import models
from general_ledger.managers.transaction_entry import EntryQuerySet
from general_ledger.django.models import Direction, Entry
from general_ledger.django.models.ledger import Ledger
from general_ledger.django.models.account import Account
from general_ledger.utils.inspect import inspect


class LedgerAccount(models.Manager):
    """
    instance of an account on a specific ledger
    """

    has_summary: bool = False
    _entry_set: EntryQuerySet = None
    #  = field(default_factory=lambda: str(uuid.uuid4()))

    def get_queryset(self):
        qs = Entry.objects.filter(
            transaction__ledger=self.ledger,
            account=self.account,
        )
        return qs

    def __init__(self, ledger, account):
        self.ledger: Ledger = ledger
        self.account: Account = account
        super().__init__()

    @property
    def entry_set(self):
        if self._entry_set is None:
            self._entry_set = self.account.entry_set.filter(
                transaction__ledger=self.ledger
            )
        return self._entry_set

    @property
    def account_name(self):
        return self.account.name

    @property
    def code(self):
        return self.account.code

    @property
    def currency(self):
        return self.account.currency

    @property
    def balance(self):
        if self.account.direction == Direction.DEBIT:
            return self.entry_set.debit_balance()
        else:
            return self.entry_set.credit_balance()
