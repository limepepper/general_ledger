from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class UserBookAccess(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    book = models.ForeignKey("general_ledger.Book", on_delete=models.CASCADE)
    is_read_only = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        try:
            user = getattr(self, "user", "None")
        except ObjectDoesNotExist:
            user = "None"
        try:
            book = getattr(self, "book", "None")
        except ObjectDoesNotExist:
            book = "None"
        return f"{user} - {book}"
