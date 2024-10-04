from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from timezone_field.rest_framework import TimeZoneSerializerField

from general_ledger.models import Contact, Bank


class BankAccountSerializer(serializers.HyperlinkedModelSerializer):
    #tz = TimeZoneSerializerField()

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
