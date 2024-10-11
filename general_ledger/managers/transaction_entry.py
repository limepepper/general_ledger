import logging

from django.db import models

from general_ledger.models import Direction
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)


class EntryQuerySet(models.QuerySet):
    def debit_balance(self):
        return sum([entry.amount for entry in self.filter(tx_type=Direction.DEBIT)])

    def credit_balance(self):
        return sum([entry.amount for entry in self.filter(tx_type=Direction.CREDIT)])

    def balance(self):
        return self.debit_balance() - self.credit_balance()


class EntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("account", "transaction")
