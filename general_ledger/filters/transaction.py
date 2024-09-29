import django_filters
from django import forms

from general_ledger.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="trans_date",
        lookup_expr="gte",
        label="Date From",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    end_date = django_filters.DateFilter(
        field_name="trans_date",
        lookup_expr="lte",
        label="Date To",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Transaction
        fields = ("start_date", "end_date")
