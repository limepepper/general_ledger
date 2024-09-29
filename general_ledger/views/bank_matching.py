from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView
from django_filters.views import FilterView
from rich import inspect

from general_ledger.forms.matching_xfer import TransferForm
from general_ledger.forms.payment import PaymentCreateForm
from general_ledger.forms.payment_edit import PaymentEditForm
from general_ledger.models import BankStatementLine, Payment, Payment
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class BankReconciliation(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    # FilterView,
    ListView,
):

    model = BankStatementLine
    template_name = "gl/bank/bank_transaction_reconciliation.html.j2"
    context_object_name = "banks"
    paginate_by = 10

    def get_queryset(self):
        bank_id = self.kwargs.get("bank_id")
        return BankStatementLine.objects.filter(
            bank_id=bank_id,
            is_reconciled=False,
        )

    # def get_context_object_name(self, object_list):
    #     return "transactions"
    def get_form_kwargs(self):
        # dLogger.debug("ContactUpdateView : get_form_kwargs")
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        # dLogger.debug(f"ContactUpdateView : get_form_kwargs kwargs: {kwargs}")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bank_id"] = self.kwargs.get("bank_id")
        print(f"queryset length: {len(context['banks'])}")
        forms = {}
        xfer_form = {}
        for line in context["banks"]:
            forms[str(line.id)] = PaymentCreateForm(
                instance=line,
                prefix=f"form_{line.id}",
                active_book_id=self.request.active_book.id,
            )
            line.form = forms[str(line.id)]

            if line.get_payments().count() > 0:
                # forms[str(line.id)].fields["payment"].queryset = line.get_payments()
                line.form_match = PaymentEditForm(
                    instance=line.get_payments().first(),
                    prefix=f"form_{line.id}",
                )
            xfer_form[str(line.id)] = TransferForm(
                instance=line,
                prefix=f"form_{line.id}",
                active_book_id=self.request.active_book.id,
            )
            line.xfer_form = xfer_form[str(line.id)]
        return context


class BankTxMatchedEditView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    UpdateView,
):

    model = Payment
    form_class = PaymentEditForm
    # template_name = "gl/bank_transaction_reconciliation.html.j2"
    context_object_name = "tx"

    def form_valid(self, form):
        print("BankTxMatchedEditView - calling form_valid")
        response = super().form_valid(form)
        return response

    def post(self, request, *args, **kwargs):
        print("BankTxMatchedEditView - calling post")
        self.prefix = request.POST.get("prefix")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.POST.get("next")

        # reverse("general_ledger:bank-reconciliation", kwargs={"bank_id": self.object.bank_id})
