import django_filters

from general_ledger.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    invoice_number = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Invoice
        fields = ["name", "invoice_number"]
