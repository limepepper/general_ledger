from datetime import date
from decimal import Decimal

from django.db import models
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)
from general_ledger.models.mixins import (
    BusinessAccountsMixin,
    LinksMixin,
    ValidatableModelMixin,
    EditableMixin,
)

# this is a bunch of app specific mixins


class InvoiceBaseMixin(
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
    BusinessAccountsMixin,
    LinksMixin,
    ValidatableModelMixin,
    EditableMixin,
):
    """
    Mixin that sets a base invoice property
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    # this is the ledger that the invoice txs gets posted to
    ledger = models.ForeignKey(
        "Ledger",
        on_delete=models.CASCADE,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    invoice_number = models.CharField(
        max_length=20,
        unique=True,
    )

    @property
    def name(self):
        return self.invoice_number

    date = models.DateField(
        default=date.today,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    contact = models.ForeignKey(
        "Contact",
        on_delete=models.CASCADE,
        limit_choices_to={"is_customer": True},
    )

    tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
    )

    def recalculate_amount(self):
        try:
            self.amount = self.total_inclusive()
        except Exception as e:
            logger.error(f"error calculating total amount {e}")

    def total_inclusive(self):
        """
        Calculate the total invoice amount including tax.
        """
        return Decimal(
            sum(line.line_total_inclusive() for line in self.invoice_lines.all())
        )
