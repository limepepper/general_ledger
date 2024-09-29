from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive




class BusinessAccountsMixin(models.Model):
    """
    Mixin that sets optional business accounts
    """

    sales_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    sales_tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    sales_tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    purchases_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    purchases_tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    purchases_tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    accounts_receivable = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    accounts_payable = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
