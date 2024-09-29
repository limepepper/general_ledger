from rest_framework import permissions, viewsets

from general_ledger.models import Invoice, Payment
from general_ledger.serializers.invoice import InvoiceSerializer
from general_ledger.serializers.payment import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
