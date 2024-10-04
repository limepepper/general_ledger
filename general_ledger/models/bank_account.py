import logging
from decimal import Decimal
from uuid import uuid4

from django.db import models

from general_ledger.managers.bank import BankManager
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    SlugMixin,
)
from general_ledger.models.mixins import LinksMixin


class Bank(
    CreatedUpdatedMixin,
    SlugMixin,
    LinksMixin,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    objects = BankManager()

    class Meta:
        db_table = "gl_bank"
        verbose_name = "Bank"
        verbose_name_plural = "Banks"
        ordering = ["name"]
        unique_together = ["book", "slug"]

    # generic view class attributes
    links_detail = "general_ledger:bank-detail"
    links_list = "general_ledger:bank-list"
    links_create = "general_ledger:bank-create"
    links_edit = "general_ledger:bank-update"
    links_title_field = "name"

    generic_list_display = (
        "link",
        "type",
        "account_number",
        "sort_code",
    )

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    id = models.UUIDField(
        default=uuid4,
        # @TODO any way to avoid this as it makes it show
        # up in the admin interface
        # editable=False,
        unique=True,
        primary_key=True,
    )

    account = models.OneToOneField(
        "Account",
        on_delete=models.CASCADE,
        related_name="bank_account",
    )

    name = models.CharField(
        max_length=255,
    )

    account_number = models.CharField(
        max_length=20,
        unique=True,
    )

    routing_number = models.CharField(
        max_length=20,
        unique=False,
        null=True,
        blank=True,
    )
    sort_code = models.CharField(
        max_length=20,
        unique=False,
        null=True,
    )

    CHECKING = "CH"
    SAVINGS = "SA"
    TYPE_CHOICES = {
        CHECKING: "Checking",
        SAVINGS: "Savings",
    }

    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=CHECKING,
    )

    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.account_number}/{self.sort_code}"

    def get_balance(self):
        try:
            return self.bankbalance_set.latest("balance_date").balance
        except:
            return Decimal(0.0)

    def get_unmatched_count(self):
        return self.bankstatementline_set.filter(is_matched=False).count()

    def get_unreconciled_count(self):
        return self.bankstatementline_set.filter(is_reconciled=False).count()
