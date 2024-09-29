from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Invoice, Ledger


# Serializers define the API representation.
class LedgerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ledger
        # fields = "__all__"
        fields = [
            "id",
            "name",
            "description",
            "is_posted",
            "created_at",
            "updated_at",
        ]
