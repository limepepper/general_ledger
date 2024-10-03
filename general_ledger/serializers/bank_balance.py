from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import BankStatementLine, BankBalance


class BankBalanceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = BankBalance
        # fields = "__all__"
        fields = [
            "balance_date",
            "balance",
        ]
