from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class InvoiceTransaction(models.Model):
    """
    This is a through model for the many to many relationship between invoices and transactions
    """

    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.CASCADE,
    )
    transaction = models.ForeignKey(
        "Transaction",
        on_delete=models.CASCADE,
    )

    # transaction = models.OneToOneField(Transaction,    on_delete=models.CASCADE, related_name='invoice_transaction')
    class Meta:
        unique_together = ["invoice", "transaction"]

    def __str__(self):
        try:
            transaction = getattr(self, "transaction", "None")
        except ObjectDoesNotExist:
            transaction = "None"
        try:
            invoice = getattr(self, "invoice", "None")
        except ObjectDoesNotExist:
            invoice = "None"
        return f"{invoice} - {transaction}"
