import logging

from django.db import models

from general_ledger.models import Direction
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)


class AccountTypeQuerySet(models.QuerySet):
    pass

class AccountTypeManager(models.Manager):
    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )

    def for_ledger(self, ledger):
        return self.get_queryset().filter(
            book=ledger.book,
        )

    def get_by_natural_key(self, slug, book):
        return self.get(
            slug=slug,
            book=book,
        )
