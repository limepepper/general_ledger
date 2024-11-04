from datetime import timedelta

import rich.repr
from django.db import models
from loguru import logger

from general_ledger.managers.ledger_manager import LedgerManager, LedgerQuerySet
from general_ledger.django.models.direction import Direction
from general_ledger.django.models.mixins import (
    CreatedUpdatedMixin,
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)
from general_ledger.django.models.transaction_entry import Entry


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

    @property
    def account_set(self):
        return self.coa.account_set

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

    # def __str__(self):
    #     return super(CreatedUpdatedMixin, self).__str__()

    def inventory_accounts(self):
        return self.account_set.filter(
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
        """
        get the balance for all accounts of a given type
        defaults to closing balance, but can be set to opening
        :param type_slug:
        :param balance_date:
        :param balance_at_close:
        :return:
        """
        accounts = self.account_set.filter(
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
        accounts = self.account_set.filter(
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
        return sum(
            [
                self.balance_for_account(account, balance_date, balance_at_close)
                for account in accounts
            ]
        )

    def balance_for_account(
        self,
        account,
        balance_date=None,
        balance_at_close=True,
    ):
        combined_entries = Entry.objects.filter(
            transaction__ledger=self,
            account=account,
        )
        if not balance_at_close:
            balance_date = balance_date - timedelta(days=1)

        if balance_date:
            combined_entries = combined_entries.filter(
                transaction__trans_date__lte=balance_date,
            )

        direction = account.direction
        logger.trace(f"direction: {direction} ")

        if direction == Direction.DEBIT:
            balance = combined_entries.debit_balance()
        else:
            balance = combined_entries.credit_balance()

        return balance

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.name
        yield "book", self.book if self.book_id else None
        yield "coa", self.coa if self.coa_id else None
        yield "description", self.description, None
        yield "id", self.id
        yield "slug", self.slug
        yield "is_posted", self.is_posted, False
        yield "is_locked", self.is_locked, False
        yield "is_system", self.is_system, False
        yield "is_hidden", self.is_hidden, False
        if self.coa_id:
            yield "accounts", self.coa.account_set.all().count()
        if hasattr(self, "transaction_set"):
            yield "transactions", self.transaction_set.count()
        if hasattr(self, "_state"):
            yield "adding", self._state.adding, False

    # __rich_repr__.angular = True

    # def __rich_console__(
    #     self, console: Console, options: ConsoleOptions
    # ) -> RenderResult:
    #     yield "rgeijerog"
