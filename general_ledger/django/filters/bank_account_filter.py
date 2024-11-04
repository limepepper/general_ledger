import django_filters
import timezone_field
from django_filters import rest_framework as filters

from general_ledger.django.models import Bank


class BankAccountFilter(filters.FilterSet):
    class Meta:
        model = Bank
        fields = ["name", "account_number", "sort_code"]
        filter_overrides = {
            timezone_field.TimeZoneField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }
