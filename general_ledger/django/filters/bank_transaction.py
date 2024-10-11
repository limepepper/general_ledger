import uuid

from django_filters import rest_framework as filters

from general_ledger.django.models import BankStatementLine


class UUIDFilter(filters.UUIDFilter):
    def filter(self, qs, value):
        if value:
            try:
                uuid.UUID(str(value))
                return super().filter(qs, value)
            except ValueError:
                return qs.none()
        return qs


class BankStatementFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")
    bank_id = UUIDFilter(field_name="bank__id")

    class Meta:
        model = BankStatementLine
        fields = [
            "start_date",
            "end_date",
            "bank_id",
        ]
