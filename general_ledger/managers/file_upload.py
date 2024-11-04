from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from forex_python.converter import CurrencyCodes

from general_ledger.django.models.tax_rate import TaxRate


class FileUploadManager(models.Manager):
    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )
