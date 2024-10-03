import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Window, Sum
from forex_python.converter import CurrencyCodes

from general_ledger.managers.account import AccountManager
from general_ledger.models.direction import Direction
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    UuidMixin,
    SlugMixin,
    LinksMixin,
)


class Account(
    UuidMixin,
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    LinksMixin,
    SlugMixin,
):

    logger = logging.getLogger(__name__)

    objects = AccountManager()

    class Meta:
        db_table = "gl_account"
        verbose_name_plural = "accounts"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "coa"], name="name_coa_uniq"),
            models.UniqueConstraint(fields=["slug", "coa"], name="slug_coa_uniq"),
        ]

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
        # limit_choices_to=Q(book=OuterRef("book")),
        # limit_choices_to=limit1,
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        # print(f"self.account_type: xxx {self.account_type}")
        quote = "'"
        obrack = "("
        cbrack = ")"
        try:
            name = getattr(self.type, "name", "None")
        except ObjectDoesNotExist:
            name = "None"
        return f"{quote+self.name+quote: <25} {obrack+name+cbrack: <25}"

        # constraints = [
        #     UniqueConstraint(
        #         fields=["code"],
        #         condition=Q(code__isnull=False) & ~Q(code=""),
        #         name="unique_non_empty_code",
        #     )
        # ]

    def get_debit_balance(self):
        return sum(
            [entry.amount for entry in self.entry_set.filter(tx_type=Direction.DEBIT)]
        )

    def get_credit_balance(self):
        return sum(
            [entry.amount for entry in self.entry_set.filter(tx_type=Direction.CREDIT)]
        )

    def get_balance(self):
        debit_balance = self.get_debit_balance()
        credit_balance = self.get_credit_balance()
        amount = debit_balance - credit_balance

        # entries = self.entry_set.select_related('transaction').annotate(
        #     running_balance=Window(
        #         expression=Sum('amount'),
        #         #expression=Coalesce(Sum('amount'), 0),
        #         order_by=[F('transaction__trans_date').asc()],
        #         #frame=Window.frames.RowRange(start=Window.start, end=0)
        #     )
        # )

        print(f"debit sum{self.entry_set.filter(tx_type=Direction.DEBIT)}")

        # print(amount)
        return amount

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

    # def get_balance(self):
    #     amount = Entry.objects.filter(account=self).aggregate(models.Sum("amount"))[
    #         "amount__sum"
    #     ]
    #     print(amount)
