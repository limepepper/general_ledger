from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Invoice
from general_ledger.serializers.invoice_line import InvoiceLineSerializer
from general_ledger.serializers.transaction import TransactionSerializer


# Serializers define the API representation.
class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
    invoice_lines = InvoiceLineSerializer(many=True, read_only=False)
    # transactions = TransactionSerializer(many=True, read_only=False)

    class Meta:
        model = Invoice
        # fields = "__all__"
        fields = [
            "url",
            "id",
            "get_absolute_url",
            "slug",
            "sales_tax_inclusive",
            "invoice_lines",
            "invoice_number",
            "amount",
            "date",
            "due_date",
            "contact",
            "status",
            "bank_account",
            "sales_account",
            # "transactions",
            "updated_at",
            "created_at",
            "total_amount",
            "purchases_account",
            # "sales_tax_rate",
        ]
