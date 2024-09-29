import logging
from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from general_ledger.models import Account, TaxRate, AccountType
from general_ledger.models.mixins import LinksMixin
from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)


class BankManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
            is_active=True,
        )

    def create_with_account(
        self,
        name,
        book,
        account_number,
        sort_code,
        code=None,
        **kwargs,
    ):
        coa = book.get_default_coa()
        account, created = Account.objects.get_or_create(
            name=name,
            coa=coa,
            tax_rate=TaxRate.objects.get(
                slug="no-vat",
                book=book,
            ),
            type=AccountType.objects.get(
                name="Bank",
                book=book,
            ),
            **kwargs,
        )

        bank, created = self.get_or_create(
            name=name,
            book=book,
            account_number=account_number,
            sort_code=sort_code,
            id=account,
            **kwargs,
        )
        return (
            bank,
            account,
        )
