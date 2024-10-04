from uuid import UUID

from django.db import models
from django.db.models import Q
from loguru import logger
from rich import inspect

from general_ledger.models import Account, TaxRate, AccountType


# LOGGING_CONSOLE = Console(
#     file=sys.stderr,
# )


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

    def search(self, query):
        try:
            uuid_value = UUID(query)
        except (ValueError, TypeError) as e:
            uuid_value = None

        filter_condition = Q(slug__iexact=query) | Q(name__icontains=query)

        if uuid_value:
            filter_condition |= Q(pk=uuid_value)

        return self.get_queryset().get(filter_condition)

    def filter_kwargs(self, **kwargs):
        # Account = apps.get_model('general_ledger', 'Account')
        model_fields = [field.name for field in self.model._meta.get_fields()]
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in model_fields
        }
        return filtered_kwargs

    def create_with_account(
        self,
        book,
        bank_id=None,
        **kwargs,
    ):
        """
        Create a Bank instance with an associated Account instance
        """

        bank_type = kwargs.pop("type", None)

        filtered_account_kwargs = Account.objects.filter_kwargs(**kwargs)
        # inspect(filtered_account_kwargs, title="filtered_account_kwargs")
        account_defaults = {
            "name": kwargs.get("name"),
            "tax_rate": TaxRate.objects.get(
                slug="no-vat",
                book=book,
            ),
            "type": AccountType.objects.get(
                name="Bank",
                book=book,
            ),
            "coa": book.get_default_coa(),
        }
        account_defaults.update(filtered_account_kwargs)

        # logger.debug(account_defaults)

        # inspect(bank_id, title="bank_id")
        if bank_id:
            try:
                existing_pk = Account.objects.get(bank_account=bank_id).pk
            except Account.DoesNotExist:
                existing_pk = None
        else:
            existing_pk = None

        account, account_created = Account.objects.update_or_create(
            id=existing_pk,
            defaults=account_defaults,
        )

        filtered_bank_kwargs = self.filter_kwargs(**kwargs)
        if bank_type:
            filtered_bank_kwargs.update({"type": bank_type})
        bank, bank_created = self.update_or_create(
            id=bank_id,
            book=book,
            account=account,
            defaults=filtered_bank_kwargs,
        )

        logger.info(
            f"Bank: '{bank}' / [{bank_created}] Account: '{account}' / [{account_created}]"
        )

        return bank
