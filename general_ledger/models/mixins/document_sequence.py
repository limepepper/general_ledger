from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive



class DocumentSequencePrefixMixin(models.Model):
    """
    Mixin that sets allows setting prefixes and sequence numbers for documents
    """

    invoice_sequence = models.PositiveIntegerField(
        default=1,
        help_text="The next number to use for invoices",
    )
    invoice_prefix = models.CharField(
        max_length=10,
        default="INV",
        help_text="The prefix to use for invoices",
    )

    bill_sequence = models.PositiveIntegerField(
        default=1,
        help_text="The next number to use for bills",
    )

    bill_prefix = models.CharField(
        max_length=10,
        default="BILL",
        help_text="The prefix to use for Bill numbers",
    )

    class Meta:
        abstract = True
