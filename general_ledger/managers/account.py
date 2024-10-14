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


class AccountQuerySet(models.QuerySet):

    def current_asset(self):
        return self.filter(
            type__category=AccountType.Category.ASSET_CURRENT,
        )

    def non_current_asset(self):
        return self.filter(
            type__category=AccountType.Category.ASSET_NON_CURRENT,
        )

    def asset(self):
        return self.filter(
            type__category__in=[
                AccountType.Category.ASSET_CURRENT,
                AccountType.Category.ASSET_NON_CURRENT,
            ],
        )

    def current_liability(self):
        return self.filter(
            type__category=AccountType.Category.LIABILITY_CURRENT,
        )

    def non_current_liability(self):
        return self.filter(
            type__category=AccountType.Category.LIABILITY_NON_CURRENT,
        )

    def liability(self):
        return self.filter(
            type__category__in=[
                AccountType.Category.LIABILITY_CURRENT,
                AccountType.Category.LIABILITY_NON_CURRENT,
            ],
        )

    def inventory(self):
        return self.filter(
            type__slug="inventory",
        )

class AccountManager(models.Manager):
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

    def filter_kwargs(self, **kwargs):
        account_fields = [field.name for field in self.model._meta.get_fields()]
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in account_fields
        }
        return filtered_kwargs
