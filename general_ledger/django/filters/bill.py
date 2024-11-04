import django_filters

from general_ledger.django.models import Contact
from general_ledger.django.models.invoice_purchaseinvoice import PurchaseInvoice


class BillFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    bill_number = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = PurchaseInvoice
        fields = ["name", "bill_number"]
