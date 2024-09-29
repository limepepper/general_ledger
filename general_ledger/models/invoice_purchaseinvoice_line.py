import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger
from rich import inspect

from general_ledger.managers.invoice_line import InvoiceLineManager
from general_ledger.models.invoice_line_base import InvoiceLineBase
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
)


class PurchaseInvoiceLine(
    InvoiceLineBase,
):
    """
    Can track inventory, sales, discounts etc
    """

    logger = logging.getLogger(__name__)

    # objects = InvoiceLineManager()

    class Meta:
        verbose_name = "Bill Line Item"
        verbose_name_plural = "Bill Line Item"
        db_table = "gl_purchaseinvoice_line_item"

    invoice = models.ForeignKey(
        "PurchaseInvoice",
        related_name="lines",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        logger.trace(f"LineItem.save: {self}")
        self.full_clean()
        if self._state.adding:
            logger.trace(f"LineItem adding: {self}")
            last_order = PurchaseInvoiceLine.objects.filter(
                invoice=self.invoice
            ).aggregate(models.Max("order"))["order__max"]
            self.order = last_order + 1 if last_order is not None else 1
        super().save(*args, **kwargs)

    def can_edit(self):
        return all(
            [
                self.invoice.can_edit(),
            ]
        )
