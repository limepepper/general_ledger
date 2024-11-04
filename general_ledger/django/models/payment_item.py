from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PaymentItem(models.Model):
    payment = models.ForeignKey(
        "Payment",
        on_delete=models.CASCADE,
        related_name="items",
    )
    amount = models.DecimalField(
        max_digits=16,
        decimal_places=4,
    )
    from_content_type = models.ForeignKey(
        ContentType,
        related_name="payment_from",
        on_delete=models.CASCADE,
    )
    from_object_id = models.UUIDField()
    from_object = GenericForeignKey(
        "from_content_type",
        "from_object_id",
    )
    from_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
    )
    to_content_type = models.ForeignKey(
        ContentType,
        related_name="payment_to",
        on_delete=models.CASCADE,
    )

    to_object_id = models.UUIDField()
    to_object = GenericForeignKey(
        "to_content_type",
        "to_object_id",
    )
    to_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="+",
    )
