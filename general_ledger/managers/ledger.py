from django.apps import apps
from django.db import models

from general_ledger.managers.mixins import CommonBooleanMixins
from general_ledger.models.account import Account
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    NameDescriptionMixin,
    UuidMixin,
    SlugMixin,
)


class LedgerQuerySet(CommonBooleanMixins):
    pass


class LedgerManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        """
        get all ledgers for a book
        :param book:
        :return:
        """
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

