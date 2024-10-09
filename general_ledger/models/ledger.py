from django.apps import apps
from django.db import models

from general_ledger.managers.ledger import LedgerManager, LedgerQuerySet
from general_ledger.models.account import Account
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)


class Ledger(
    UuidMixin,
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    SlugMixin,
):
    """
    This class demonstrates various ways of linking in docstrings.

    It references :class:`general_ledger.admin.LedgerAdmin` and :func:`utility_function`.

    Attributes:
        attribute1 (int): An example attribute.

        `My cool link <http://www.asdf.com>`_
    """

    objects = LedgerManager.from_queryset(LedgerQuerySet)()

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # this is redundant as the relationship is available through the CoA
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    coa = models.ForeignKey(
        "ChartOfAccounts",
        on_delete=models.CASCADE,
    )

    is_posted = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ledger"
        verbose_name_plural = "Ledgers"
        db_table = "gl_ledger"
        unique_together = [
            ["slug", "book"],
            ["name", "book"],
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name
