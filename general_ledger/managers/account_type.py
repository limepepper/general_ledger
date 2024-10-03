import logging

from django.db import models

from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)


class AccountTypeManager(models.Manager):
    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )

    def for_ledger(self, ledger):
        return self.get_queryset().filter(
            book=ledger.book,
        )

    def natural_key(self):
        return self.slug, self.book
