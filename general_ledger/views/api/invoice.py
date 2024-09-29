from rest_framework import permissions, viewsets

from general_ledger.models import Invoice
from general_ledger.serializers.invoice import InvoiceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
