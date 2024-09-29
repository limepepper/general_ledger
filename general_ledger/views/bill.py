from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django_filters.views import FilterView

from general_ledger.filters import BillFilter
from general_ledger.models import PurchaseInvoice
from general_ledger.views.mixins import ActiveBookRequiredMixin
from general_ledger.views.mixins import GeneralLedgerSecurityMixIn


class BillListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    ListView,
):

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["active_book"] = self.request.active_book
        return data

    def get_queryset(self):
        return PurchaseInvoice.objects.for_book(self.request.active_book)

    model = PurchaseInvoice
    template_name = "gl/bill/bill_list.html.j2"
    context_object_name = "bills"
    paginate_by = 25
    filterset_class = BillFilter


class BillCreateView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    CreateView,
):
    model = PurchaseInvoice
    template_name = "gl/invoice/invoice_form.html.j2"
    fields = ["name"]
    success_url = reverse_lazy("general_ledger:invoice-list")
