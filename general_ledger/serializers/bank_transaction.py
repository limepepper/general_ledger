from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import serializers


class BankStatementGroupedSerializer(
    serializers.Serializer,
):
    date = serializers.DateField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=4,
    )
