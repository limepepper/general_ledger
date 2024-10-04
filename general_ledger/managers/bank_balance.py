import logging

from django.db import models

from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
)


class BankBalanceManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "bank",
        )

    def for_bank(self, bank):
        return self.get_queryset().filter(
            bank=bank,
        )

