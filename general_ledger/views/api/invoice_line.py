from rest_framework import permissions, viewsets

from general_ledger.models import Invoice, InvoiceLine
from general_ledger.serializers.invoice import InvoiceSerializer
from general_ledger.serializers.invoice_line import InvoiceLineSerializer


class InvoiceLineViewSet(viewsets.ModelViewSet):
    queryset = InvoiceLine.objects.all()
    serializer_class = InvoiceLineSerializer
    permission_classes = [permissions.IsAuthenticated]
