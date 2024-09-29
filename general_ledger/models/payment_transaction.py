from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class PaymentTransaction(models.Model):
    """
    This is a through model for the many to many relationship between payments and transactions
    """

    payment = models.ForeignKey(
        "Payment",
        on_delete=models.CASCADE,
    )
    transaction = models.ForeignKey(
        "Transaction",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = [
            "payment",
            "transaction",
        ]

    def __str__(self):
        try:
            transaction = getattr(self, "transaction", "None")
        except ObjectDoesNotExist:
            transaction = "None"
        try:
            payment = getattr(self, "payment", "None")
        except ObjectDoesNotExist:
            payment = "None"
        return f"{payment} - {transaction}"
