import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger
from rich import inspect

from general_ledger.managers.invoice_line import InvoiceLineManager
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
)


class InvoiceLine(
    UuidMixin,
    NameDescriptionMixin,
):
    """
    Can track inventory, sales, discounts etc
    """

    logger = logging.getLogger(__name__)

    objects = InvoiceLineManager()

    class Meta:
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"
        db_table = "gl_line_item"
        ordering = ["order"]

    name = models.CharField(
        max_length=100,
        blank=True,
    )

    invoice = models.ForeignKey(
        "Invoice",
        related_name="invoice_lines",
        on_delete=models.CASCADE,
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=0,
    )

    unit_price = models.DecimalField(
        max_digits=16,
        decimal_places=4,
    )

    # to support line item type account specificity
    account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    vat_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
    )

    # preserving the original order of the line items
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.unit_price} of {self.description}"

    def clean(self):
        if self.pk:
            if not self.invoice.can_edit():
                raise ValidationError("Cannot modify lines of a recorded invoice.")

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=["id", "invoice"])

    def delete(self, *args, **kwargs):
        if not self.invoice.can_edit():
            raise ValidationError("Cannot delete lines from a recorded invoice.")
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        logger.trace(f"LineItem.save: {self}")
        self.full_clean()
        if self._state.adding:
            logger.trace(f"LineItem adding: {self}")
            last_order = InvoiceLine.objects.filter(invoice=self.invoice).aggregate(
                models.Max("order")
            )["order__max"]
            self.order = last_order + 1 if last_order is not None else 1
        super().save(*args, **kwargs)

    #
    # stuff to do with calculating the line total
    #

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def line_total_exclusive(self):
        """
        calculate the line total exclusive of tax. also return
        the account if available
        :return:
        """
        if TaxInclusive(self.invoice.tax_inclusive) == TaxInclusive.INCLUSIVE:
            # return self.line_total / (1 + self.vat_rate.rate)
            # Calculate net price if the unit price includes tax
            tax_multiplier = Decimal(1) + self.vat_rate.rate
            unit_price_exclusive = self.unit_price / tax_multiplier
            line_total = Decimal(unit_price_exclusive * self.quantity)
            # print(f"line_total: {self.line_total} {type(self.line_total)}")
            return (
                line_total,
                self.account,
            )
        # elif self.invoice.tax_inclusive == TaxInclusive.EXCLUSIVE:
        else:
            # Unit price is already exclusive of tax if tax is exclusive or none
            return (
                Decimal(self.line_total),
                self.account,
            )

    def tax_amount(self):
        """
        Calculate the tax amount for this line.
        """
        if TaxInclusive(self.invoice.tax_inclusive) == TaxInclusive.INCLUSIVE:
            # Tax is already included in unit price, we need to extract it
            tax_multiplier = Decimal(1) + self.vat_rate.rate
            unit_price_exclusive = self.unit_price / tax_multiplier
            tax_amount = (self.unit_price - unit_price_exclusive) * self.quantity
        elif TaxInclusive(self.invoice.tax_inclusive) == TaxInclusive.EXCLUSIVE:
            # Tax is not included in unit price, calculate tax based on exclusive price
            tax_amount = self.line_total_exclusive()[0] * self.vat_rate.rate
        else:
            # No tax - ignore any supplied tax rate
            tax_amount = Decimal(0)

        return (
            tax_amount,
            self.vat_rate,
        )

    def line_total_inclusive(self):
        """
        Calculate the line total including tax.
        """
        if TaxInclusive(self.invoice.tax_inclusive) == TaxInclusive.INCLUSIVE:
            # The unit price already includes tax
            line_total = Decimal(self.unit_price * self.quantity)
        else:
            # Calculate inclusive price
            line_total = Decimal(self.line_total_exclusive()[0] + self.tax_amount()[0])

        return line_total
