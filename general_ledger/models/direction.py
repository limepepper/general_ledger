from django.db import models
from django.utils.translation import gettext_lazy as _


class Direction(models.TextChoices):
    DEBIT = "Dr", _("Debit")
    CREDIT = "Cr", _("Credit")

    def opposite(self):
        if self == Direction.DEBIT:
            return Direction.CREDIT
        return Direction.DEBIT
