from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import serializers

from general_ledger.models import BankStatementLine
import uuid


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
