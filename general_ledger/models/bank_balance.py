import logging

from django.db import models

from general_ledger.managers.bank_balance import BankBalanceManager
from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
)


class BankBalance(
    UuidMixin,
    CreatedUpdatedMixin,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    objects = BankBalanceManager()

    class Meta:
        db_table = "gl_bank_balance"
        verbose_name = "Bank Balance"
        verbose_name_plural = "Bank Balances"
        ordering = ["balance_date"]

    bank = models.ForeignKey(
        "Bank",
        on_delete=models.CASCADE,
    )

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=False,
    )
    balance_date = models.DateTimeField(
        null=False,
    )

    # informal field noting which source the balance was taken from
    # e.g. "last bank statement", "last reconciliation"
    balance_source = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    balance_type = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
