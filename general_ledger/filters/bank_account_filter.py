import django_filters
import timezone_field
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import serializers

from general_ledger.models import BankStatementLine, Bank
import uuid



class BankAccountFilter(filters.FilterSet):
    class Meta:
        model = Bank
        fields = ['name', 'account_number', 'sort_code']
        filter_overrides = {
            timezone_field.TimeZoneField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }