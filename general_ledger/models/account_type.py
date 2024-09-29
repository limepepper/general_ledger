import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from general_ledger.models.mixins import NameDescriptionMixin, UuidMixin, SlugMixin
from .direction import Direction


class AccountType(
    UuidMixin,
    SlugMixin,
    NameDescriptionMixin,
):

    logger = logging.getLogger(__name__)

    class Meta:
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"
        db_table = "gl_account_type"
        ordering = ["name"]
        unique_together = [
            [
                "slug",
                "book",
            ],
        ]

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=100)

    @property
    def direction(self) -> Direction:
        if self.category in [
            self.Category.ASSET,
            self.Category.EXPENSE,
        ]:
            return Direction.DEBIT
        return Direction.CREDIT

    class Category(models.TextChoices):
        ASSET = "A", _("Asset")
        LIABILITY = "L", _("Liability")
        EQUITY = "E", _("Equity")
        REVENUE = "R", _("Revenue")
        EXPENSE = "X", _("Expense")

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.ASSET,
    )

    is_deprecated = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name
