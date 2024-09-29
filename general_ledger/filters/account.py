import django_filters

from general_ledger.models import Contact, Account


class AccountFilter(django_filters.FilterSet):
    is_system = django_filters.BooleanFilter()
    is_hidden = django_filters.BooleanFilter()
    balance = django_filters.NumberFilter()

    class Meta:
        model = Account
        fields = ["is_system", "is_hidden", "balance"]
