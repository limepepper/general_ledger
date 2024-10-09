import logging
from decimal import Decimal
from uuid import uuid4

from django.db import models
from loguru import logger
from timezone_field import TimeZoneField

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
        constraints = [
            models.UniqueConstraint(
                fields=["book", "slug"], name="bank_account_uniq_bank_slug"
            )
        ]

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

    open_date = models.DateField(
        null=True,
        blank=True,
    )

    opening_balance = models.ForeignKey(
        "BankBalance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    close_date = models.DateField(
        null=True,
        blank=True,
    )

    closing_balance = models.ForeignKey(
        "BankBalance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    """
    The name of the general ledger account associated with this
    bank. This is used to create the account and track its transaction
    in the ledger system.
    """
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

    # If bank statement lines are imported from a file which
    # does not qualify dates/times with timezone, this value will
    # be used to convert the naive datetime to a timezone aware
    # datetime.
    tz = TimeZoneField(
        default="Europe/London",
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

    def save(self, *args, **kwargs):
        logger.trace(f"BankAccount: [saving] {self._state}")
        #if self._state.adding:
        if len(self.sort_code) == 6:
            self.sort_code = f"{self.sort_code[:2]}-{self.sort_code[2:4]}-{self.sort_code[4:]}"

        super().save(*args, **kwargs)

