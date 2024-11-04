from uuid import UUID

from django.db import models
from django.db.models import Q
from rich.console import Console
from rich.console import ConsoleOptions, RenderResult
from rich.table import Table

from general_ledger.django.models.account_type import AccountType
from general_ledger.render.utility_rich import model_table_generator


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

    def filter_kwargs(self, **kwargs):
        account_fields = [field.name for field in self.model._meta.get_fields()]
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in account_fields
        }
        return filtered_kwargs

    def get_fuzzy(self, value):
        # Try to convert the value to UUID
        try:
            uuid_value = UUID(value)
            is_valid_uuid = True
        except (ValueError, TypeError) as e:
            is_valid_uuid = False

        # Create a Q object with multiple conditions
        filter_condition = Q(name__iexact=value) | Q(slug__iexact=value)

        # Add UUID condition if the value is a valid UUID
        if is_valid_uuid:
            filter_condition |= Q(pk=uuid_value)

        # Apply the filter to the queryset
        return self.get(filter_condition)

    def get_by_natural_key(self, owner, slug):
        return self.get(
            owner=owner,
            slug=slug,
        )

    def __rich_repr__(self):
        yield "AccountQuerySet", {}
        yield "Count", self.count()
        # yield "Accounts", str(self)
        yield from self.iterator()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from model_table_generator(self, self.model)


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
