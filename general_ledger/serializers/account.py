from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Account


# Serializers define the API representation.
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    # book = serializers.HyperlinkedIdentityField(
    #     view_name="general_ledger:book-detail", format="html"
    # )

    class Meta:
        model = Account
        # fields = "__all__"
        fields = [
            "id",
            "name",
        ]
