import logging

from django.db import models

from general_ledger.models.mixins import UuidMixin


class XeroGlImport(UuidMixin):

    logger = logging.getLogger(__name__)

    journal_number = models.CharField(max_length=12)
    journal_date = models.DateField()
    account_name = models.CharField(max_length=200, null=True)
    account_code = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_code = models.CharField(max_length=10, null=True)
    reference = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    bank_account_code = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name = "XeroGlImport"
        verbose_name_plural = "XeroGlImports"
        db_table = "gl_xero_gl_import"
        ordering = ["journal_date"]

    def __str__(self):
        return f"{self.journal_number} {self.journal_date} {self.account_code} {self.net_amount} {self.gst_amount} {self.gross_amount}"
