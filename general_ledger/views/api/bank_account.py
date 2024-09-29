from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Bank
from general_ledger.serializers.bank_account import BankAccountSerializer
from general_ledger.serializers.contact import ContactSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankAccountSerializer
