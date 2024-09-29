from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Bank


class BankAccountSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bank
        # fields = "__all__"
        fields = [
            # "id",
            "name",
            "account_number",
            "sort_code",
            # "book",
        ]
