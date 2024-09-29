import logging

from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView
from django_filters.views import FilterView
from formset.views import FormViewMixin

from general_ledger.forms.bank import BankForm
from general_ledger.forms.bank_transaction import BankTransactionForm
from general_ledger.models import Bank, BankStatementLine
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class BankTransactionsListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    ListView,
):

    def get_queryset(self):
        bank_id = self.kwargs.get("bank_id")
        return BankStatementLine.objects.filter(bank_id=bank_id)

    model = BankStatementLine
    template_name = "gl/bank_transaction_list.html.j2"
    context_object_name = "transactions"
    # filterset_class = BankFilter


class BankTransactionDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    DetailView,
):
    model = BankStatementLine
    template_name = "gl/bank_transaction_detail.html.j2"
    context_object_name = "transaction"


class BankTransactionUpdateView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    # IncompleteSelectResponseMixin,
    FormViewMixin,
    UpdateView,
):

    logger = logging.getLogger(__name__)

    model = BankStatementLine
    template_name = "gl/bank_transaction_form.html.j2"
    form_class = BankTransactionForm
    success_url = reverse_lazy("general_ledger:bank-transactions-list")
