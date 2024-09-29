from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Ledger
from general_ledger.serializers.contact import ContactSerializer
from general_ledger.serializers.ledger import LedgerSerializer


class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer
