import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Window, Sum
from forex_python.converter import CurrencyCodes

from general_ledger.models.account_type import AccountType
from general_ledger.models.direction import Direction
from general_ledger.models.tax_rate import TaxRate
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    UuidMixin,
    SlugMixin,
)


class FileUploadManager(models.Manager):
    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )