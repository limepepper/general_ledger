from django.db import models

from general_ledger.managers.ledger import LedgerManager, LedgerQuerySet
from general_ledger.models import Direction
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)
from general_ledger.models.transaction_entry import Entry
from datetime import datetime, timedelta


class Ledger(
    UuidMixin,
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    SlugMixin,
):
    """
    This class demonstrates various ways of linking in docstrings.

    It references :class:`general_ledger.admin.LedgerAdmin` and :func:`utility_function`.

    Attributes:
        attribute1 (int): An example attribute.

        `My cool link <http://www.asdf.com>`_
    """

    objects = LedgerManager.from_queryset(LedgerQuerySet)()

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # this is redundant as the relationship is available through the CoA
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    coa = models.ForeignKey(
        "ChartOfAccounts",
        on_delete=models.CASCADE,
    )

    is_posted = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ledger"
        verbose_name_plural = "Ledgers"
        db_table = "gl_ledger"
        unique_together = [
            ["slug", "book"],
            ["name", "book"],
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def inventory_accounts(self):
        return self.coa.account_set.filter(
            type__slug="inventory",
        )

    def inventory_balance(self):
        combined_entries = Entry.objects.filter(
            transaction__ledger=self,
            account__in=self.inventory_accounts(),
        )
        balance = combined_entries.balance()
        return balance

    def balance_by_type_slug(
        self,
        type_slug,
        balance_date=None,
        balance_at_close=True,
    ):
        accounts = self.coa.account_set.filter(
            type__slug=type_slug,
        )

        return self.balance_for_accounts(
            accounts,
            balance_date=balance_date,
            balance_at_close=balance_at_close,
        )

    def balance_by_slug(
        self,
        slug,
        balance_date=None,
        balance_at_close=True,
    ):
        accounts = self.coa.account_set.filter(
            slug=slug,
        )

        return self.balance_for_accounts(
            accounts,
            balance_date=balance_date,
            balance_at_close=balance_at_close,
        )

    def balance_for_accounts(
        self,
        accounts,
        balance_date=None,
        balance_at_close=True,
    ):
        """
        return the appropriate debit or credit balance
        this currently won't handle the case when the list
        of accounts are a mix of CREDIT/DEBIT types
        :param accounts:
        :param balance_date:
        :param balance_at_close:
        :return:
        """
        combined_entries = Entry.objects.filter(
            transaction__ledger=self,
            account__in=accounts,
        )
        if not balance_at_close:
            balance_date = balance_date - timedelta(days=1)

        if balance_date:
            combined_entries = combined_entries.filter(
                transaction__trans_date__lte=balance_date,
            )

        direction = accounts.first().type.direction
        print(f"direction: {direction} ")

        if direction == Direction.DEBIT:
            balance = combined_entries.debit_balance()
        else:
            balance = combined_entries.credit_balance()

        return balance
