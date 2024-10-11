import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from general_ledger.models.mixins import NameDescriptionMixin, UuidMixin, SlugMixin
from .direction import Direction
from ..managers.account_type import AccountTypeManager, AccountTypeQuerySet


class AccountType(
    UuidMixin,
    SlugMixin,
    NameDescriptionMixin,
):

    logger = logging.getLogger(__name__)
    objects = AccountTypeManager.from_queryset(queryset_class=AccountTypeQuerySet)()


    class Meta:
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"
        db_table = "gl_account_type"
        ordering = ["category", "liquidity", "name"]
        unique_together = [
            [
                "slug",
                "book",
            ],
        ]

    def natural_key(self):
        return self.slug, self.book

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=100)

    @property
    def direction(self) -> Direction:
        if self.category in [
            self.Category.ASSET_NON_CURRENT,
            self.Category.ASSET_CURRENT,
            self.Category.EXPENSE,
        ]:
            return Direction.DEBIT
        return Direction.CREDIT

    class Category(models.TextChoices):
        # ASSET = "A", _("Asset")
        # LIABILITY = "L", _("Liability")
        EQUITY = "E", _("Equity")
        REVENUE = "R", _("Revenue")
        EXPENSE = "X", _("Expense")
        ASSET_NON_CURRENT = "NCA", _("Non-Current Asset")
        ASSET_CURRENT = "CA", _("Current Asset")
        LIABILITY_NON_CURRENT = "NCL", _("Non-Current Liability")
        LIABILITY_CURRENT = "CL", _("Current Liability")

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )

    class Liquidity(models.IntegerChoices):
        """
        represents the liquidity of the account type when used on a balance sheet. Generally only useful for asset and liability
        """
        CASH = 100, _("Cash or Cash Equivalent")
        BANK = 90, _("Bank")
        ACCOUNTS_RECEIVABLE = 80, _("Accounts Receivable")
        ACCOUNTS_PAYABLE = 75, _("Accounts Payable")
        INVENTORY = 70, _("Inventory")
        LOANS_SOON_DUE = 65, _("Loans Due within 12 months")
        OTHER_CURRENT_ASSETS = 60, _("Other Current Assets")
        MOTOR_VEHICLES = 50, _("Motor Vehicles")
        MACHINE_EQUIPMENT = 40, _("Machinery and Equipment")
        FIXTURES_FITTINGS = 30, _("Fixtures and Fittings")
        LAND_BUILDINGS = 20, _("Land and Buildings")
        NONE = 0, _("None")

    liquidity = models.IntegerField(
        choices=Liquidity.choices,
        default=Liquidity.NONE,
    )

    is_deprecated = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name
