import logging

from django.db import models

from general_ledger.django.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)


class ChartOfAccountsManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )
