import logging

import rich.repr
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Window, Sum
from forex_python.converter import CurrencyCodes
from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.panel import Panel

from general_ledger.django.models.direction import Direction
from general_ledger.django.models.mixins import (
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    UuidMixin,
    SlugMixin,
    LinksMixin,
)
from general_ledger.managers.account import AccountManager, AccountQuerySet
from general_ledger.render.utility_rich import fmt


class Account(
    UuidMixin,
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    LinksMixin,
    SlugMixin,
):

    logger = logging.getLogger(__name__)

    objects = AccountManager.from_queryset(queryset_class=AccountQuerySet)()

    class Meta:
        db_table = "gl_account"
        verbose_name_plural = "accounts"
        ordering = ["type__category", "type__liquidity", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "coa"],
                name="name_coa_uniq",
            ),
            models.UniqueConstraint(
                fields=["slug", "coa"],
                name="slug_coa_uniq",
            ),
        ]
        # @TODO if provided, code must be unique per coa
        # constraints = [
        #     UniqueConstraint(
        #         fields=["code"],
        #         condition=Q(code__isnull=False) & ~Q(code=""),
        #         name="unique_non_empty_code",
        #     )
        # ]

    # generic view class attributes
    links_detail = "general_ledger:account-detail"
    links_list = "general_ledger:account-list"
    links_create = "general_ledger:account-create"
    links_edit = "general_ledger:account-update"
    links_title_field = "name"

    def natural_key(self):
        return self.slug, self.coa

    coa = models.ForeignKey(
        "ChartOfAccounts",
        on_delete=models.CASCADE,
    )

    code = models.CharField(
        max_length=20,
        blank=True,
    )

    # TODO: add currency field
    currency = models.CharField(
        max_length=3,
        default="GBP",
    )

    @property
    def currency_symbol(self):
        currency_codes = CurrencyCodes()
        return currency_codes.get_symbol(self.currency)

    tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
    )

    is_system = models.BooleanField(default=False)
    is_placeholder = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    type = models.ForeignKey(
        "AccountType",
        on_delete=models.CASCADE,
        # @TODO failed attempt to limit choices to book in admin
        # limit_choices_to=Q(book=OuterRef("book")),
        # limit_choices_to=limit1,
    )

    @property
    def direction(self):
        if isinstance(self.type.direction, str):
            return Direction(self.type.direction)
        return self.type.direction

    # @TODO this makes no sense if the coa that the account
    # belongs to is attached to other ledgers.
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # def __rich_console__(self, console, options):
    #     return "test"

    # entries = self.entry_set.select_related('transaction').annotate(
    #     running_balance=Window(
    #         expression=Sum('amount'),
    #         #expression=Coalesce(Sum('amount'), 0),
    #         order_by=[F('transaction__trans_date').asc()],
    #         #frame=Window.frames.RowRange(start=Window.start, end=0)
    #     )
    # )

    def calculate_running_balance(self):
        running_balance = 0
        running_balances = {}
        for entry in self.entry_set.order_by("transaction__trans_date"):
            # print(f"entry: {entry}")
            running_balance += entry.amount
            running_balances[entry.id] = running_balance
        return running_balances
        # subquery = (
        #     Entry.objects.filter(
        #         account=self,
        #         transaction__trans_date__lte=OuterRef("transaction__trans_date"),
        #         id__lte=OuterRef("id"),
        #     )
        #     .values("account")
        #     .annotate(running_total=Sum("amount"))
        #     .values("running_total")
        # )
        # return (
        #     Entry.objects.filter(account=self)
        #     .select_related("transaction")
        #     .annotate(running_balance=Subquery(subquery))
        #     .order_by("transaction__trans_date")
        # )

    def annotate_running_balance(self):
        entries = self.entry_set.select_related("transaction").annotate(
            running_balance=Window(
                expression=Sum("amount"),
                order_by=[F("transaction__trans_date").asc()],
                # frame = Window.frames.RowRange(start=Window.start, end=0)
            )
        )
        return entries

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        panel = Panel.fit(f"Hello, [red]{fmt(self.id)} \n duxk od", title=self.name)
        yield panel

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        # minW = min([len(str(self.id)), len(str(self.name)), len(str(self.code))])
        # maxW = max([len(str(self.name)), len(str(self.code))]) + 10
        # rprint(f"minW: {minW}, maxW: {maxW}")
        minW = 20
        maxW = 35
        return Measurement(
            minW,
            maxW,
        )

    # def __rich_repr__(self) -> rich.repr.Result:
    #     yield self.name
    #     yield "code", self.code, None
    #     yield "type", self.type
    #     yield "balance", self.balance
    #     yield "currency", self.currency
    #     yield "tax_rate", self.tax_rate
    #     yield "is_system", self.is_system, False
    #     yield "is_placeholder", self.is_placeholder, False
    #     yield "is_hidden", self.is_hidden, False
    #     yield "code", self.code, None

    def __str__(self):
        # print(f"self.account_type: xxx {self.account_type}")
        out = ""
        quote = "'"
        obrack = "("
        cbrack = ")"
        try:
            type_name = getattr(self.type, "name", "None")
        except ObjectDoesNotExist:
            type_name = "None"
        out += f"{quote+self.name+quote: <12} {obrack+type_name+cbrack: <12}"

        try:
            out += f" {self.slug: <10}"
        except AttributeError:
            pass

        return out
