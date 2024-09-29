from django.apps import apps
from django.db import models

from general_ledger.models.account import Account
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)


class LedgerQuerySet(models.QuerySet):
    def posted(self):
        return self.filter(
            is_posted=True,
        )

    def unposted(self):
        return self.filter(
            is_posted=False,
        )

    def locked(self):
        return self.filter(
            is_locked=True,
        )

    def unlocked(self):
        return self.filter(
            is_locked=False,
        )

    def system(self):
        return self.filter(
            is_system=True,
        )

    def not_system(self):
        return self.filter(
            is_system=False,
        )

    def hidden(self):
        return self.filter(
            is_hidden=True,
        )

    def not_hidden(self):
        return self.filter(
            is_hidden=False,
        )


class LedgerManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )

    def retrieve_account(
        self,
        defaults={},
        **kwargs,
    ):
        """
        create or retrieve an account from this ledger
        """
        # item = super().get(defaults, **kwargs)
        defaults.update(
            {
                "type": apps.get_model("Account").objects.get(
                    name__iexact=kwargs.get("type__name")
                ),
                "tax_rate": apps.get_model("TaxRate").objects.get(name="No VAT"),
            }
        )

        # type = defaults.get("type", None)
        # if not type:
        #     print(f"AccountModelManager.get_or_create2: type is None")
        #     type = AccountType.objects.get(name="Asset")
        # tax_rate = defaults.get("tax_rate", None)
        # if not tax_rate:
        #     print(f"AccountModelManager.get_or_create2: tax_rate is None")
        #     tax_rate = TaxRate.objects.get(name="No VAT")

        return Account.objects.get_or_create(defaults, **kwargs)


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
