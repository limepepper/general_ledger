import logging

from django.db import models
from django.db.models import Q

from general_ledger.managers.chart_of_accounts import ChartOfAccountsManager
from general_ledger.django.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)


class ChartOfAccounts(
    UuidMixin,
    NameDescriptionMixin,
    SlugMixin,
):

    logger = logging.getLogger(__name__)
    objects = ChartOfAccountsManager()

    class Meta:
        verbose_name = "Chart of Accounts"
        verbose_name_plural = "Charts of Accounts"
        db_table = "gl_coa"
        ordering = ["name"]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    is_system = models.BooleanField(default=False)
    is_placeholder = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        if self.book_id:
            return f"{self.name} {self.book}"
        return f"{self.name}"

    def get_sales_account(self):
        return self.account_set.get(
            name="Sales",
        )

    # @TODO this is wrong - returning accoutn instead of rate
    def get_sales_tax_rate(self):
        return self.account_set.get(
            name="Sales",
        )

    def getac(self, query):
        return self.account_set.get(
            Q(name__iexact=query) | Q(slug__iexact=query),
        )

    def get_or_create(self, name, type_slug=None, tax_rate_slug=None):
        defaults = {}
        if tax_rate_slug:
            defaults["tax_rate"] = self.book.taxrate_set.get(slug=tax_rate_slug)
        if type_slug:
            defaults["type"] = self.book.accounttype_set.get(slug=type_slug)

        acc, _ = self.account_set.update_or_create(
            name=name,
            defaults=defaults,
        )
        return acc
