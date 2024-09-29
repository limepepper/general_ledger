from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django_filters.views import FilterView
from rich import inspect

from general_ledger.forms.payment import PaymentCreateForm
from general_ledger.forms.payment_edit import PaymentEditForm
from general_ledger.models import BankStatementLine, Payment, Payment
from general_ledger.models.document_status import DocumentStatus
from general_ledger.views.generic import GenericListView
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class PaymentListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    # FilterView,
    GenericListView,
):
    model = Payment
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        return Payment.objects.filter(ledger__book=self.request.active_book)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_book"] = self.request.active_book
        return context


class PaymentDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    UpdateView,
):
    model = Payment
    context_object_name = "payment"
    template_name = "gl/payment/payment_detail.html.j2"
    form_class = PaymentEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DocumentStatus"] = DocumentStatus
        return context


class PaymentEditView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    CreateView,
):
    model = Payment
    form_class = PaymentCreateForm
    template_name = "gl/payment/payment_form.html.j2"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("general_ledger:payment-detail", kwargs={"pk": self.object.pk})

    def post1(self, request, *args, **kwargs):
        prefix = request.POST.get("prefix")
        next = request.POST.get("next")
        if prefix:
            form = PaymentCreateForm(
                request.POST,
                prefix=prefix,
                active_book_id=request.active_book.id,
                instance=BankStatementLine.objects.get(
                    id=request.POST.get(f"{prefix}-bank_statement_line")
                ),
            )
            context = form.get_context()
            if form.is_valid():
                form.save()
                return redirect(next)
            else:
                inspect(form.errors)
