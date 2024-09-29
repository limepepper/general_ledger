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


class AccountManager(models.Manager):
    # @TODO this dumb. move to helper
    def get_or_create2(self, defaults={}, **kwargs):
        defaults.update(
            {
                "type": AccountType.objects.get(name__iexact=kwargs.get("type__name")),
                "tax_rate": TaxRate.objects.get(name="No VAT"),
            }
        )

        return super().get_or_create(defaults, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "coa",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            coa__book=book,
        )

    def for_ledger(self, ledger):
        return self.get_queryset().filter(
            coa=ledger.coa,
        )

    def get_by_natural_key(self, name, book):
        return self.get(
            name=name,
            book=book,
        )
