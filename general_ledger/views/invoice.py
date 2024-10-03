import logging

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)
from django_filters.views import FilterView
from rich import inspect

from general_ledger.filters import InvoiceFilter
from general_ledger.forms import InvoiceForm, InvoiceLineFormSet
from general_ledger.forms.contact_inline import ContactInlineForm
from general_ledger.forms.invoice_status import InvoiceStatusForm
from general_ledger.models import Invoice
from general_ledger.views.generic import GenericListView, GenericDetailView
from general_ledger.views.history.history import HistoryView
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    IsEditableMixin,
)


class InvoiceListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    GenericListView,
):
    def get_queryset(self):
        return Invoice.objects.for_book(self.request.active_book)

    model = Invoice
    context_object_name = "invoices"
    paginate_by = 250
    filterset_class = InvoiceFilter


# This view has the status buttons on it
class InvoiceDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    GenericDetailView,
    UpdateView,
):
    model = Invoice
    context_object_name = "invoice"
    template_name = "gl/invoice/invoice_detail.html.j2"
    form_class = InvoiceStatusForm

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.warning(self.request, "The requested object was not found.")
            return None

    def form_valid(self, form):
        print("InvoiceDetailView - calling form_valid")
        response = super().form_valid(form)
        return response

    def get_context_data(self, **kwargs):
        print("InvoiceDetailView - calling get_context_data")
        data = super().get_context_data(**kwargs)
        inspect(self.object)
        # inspect(self.object.history.all())
        historical_records = HistoryView.get_history_queryset(
            self.request,
            history_manager=self.object.history,
            pk_name="id",
            object_id=self.object.pk,
        )
        HistoryView.set_history_delta_changes(
            self.request,
            historical_records=historical_records,
            model=self.object._meta.model,
        )

        context = {
            "historical_records": historical_records,
            "history_list_display": [],
        }
        data.update(context)
        inspect(data)
        return data

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return redirect(reverse("general_ledger:invoice-list"))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class InvoiceUpdateView(
    SuccessMessageMixin,
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    IsEditableMixin,
    UpdateView,
):
    model = Invoice
    success_message = "%(name)s was updated successfully"
    template_name = "gl/invoice/invoice_form.html.j2"
    fields = ["description"]

    def get_success_url(self):
        return reverse_lazy(
            "general_ledger:invoice-list",
            kwargs={"id": self.get_object().id},
        )

    def get_context_data(self, **kwargs):
        print("InvoiceUpdateView - calling get_context_data in create")
        data = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            invoice = data["invoice"]
            invoice_form = InvoiceForm(instance=invoice)
            formset = InvoiceLineFormSet(
                instance=invoice,
                form_kwargs={"request": self.request},
            )
            data["invoice_form"] = invoice_form
            data["formset"] = formset
            data["is_update"] = True

            form_contact = ContactInlineForm()
            data["form_contact"] = form_contact
        return data

    def post(self, request, *args, **kwargs):

        invoice = Invoice.objects.get(pk=kwargs["pk"])

        invoice_form = InvoiceForm(request.POST, instance=invoice)

        formset = InvoiceLineFormSet(
            request.POST,
            instance=invoice,
            form_kwargs={"request": request},
        )

        if invoice_form.is_valid() and formset.is_valid():
            invoice = invoice_form.save()
            formset.instance = invoice
            formset.save()
            return redirect("general_ledger:invoice-detail", pk=invoice.pk)

        form_contact = ContactInlineForm()
        return render(
            request,
            self.template_name,
            {
                "invoice_form": invoice_form,
                "formset": formset,
                "form_contact": form_contact,
            },
        )


class InvoiceCreateView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    CreateView,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    model = Invoice
    template_name = "gl/invoice/invoice_form.html.j2"
    fields = ["description"]

    def get_success_url(self):
        return reverse_lazy(
            "general_ledger:invoice-list",
            kwargs={"id": self.get_object().id},
        )

    def get_context_data(self, **kwargs):
        self.logger.debug("start of get_context_data")
        data = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            active_book = self.request.active_book
            invoice_form = InvoiceForm(
                initial={
                    "book": self.request.active_book,
                    "invoice_number": f"{active_book.invoice_prefix}-{active_book.invoice_sequence:04d}",
                },
            )
            formset = InvoiceLineFormSet(
                form_kwargs={"request": self.request},
            )
            # print(self.get_context_data())
            data["invoice_form"] = invoice_form
            data["formset"] = formset
            data["is_update"] = False

            form_contact = ContactInlineForm()
            data["form_contact"] = form_contact
        elif self.request.method == "POST":
            invoice_form = InvoiceForm(self.request.POST)
            formset = InvoiceLineFormSet(
                self.request.POST,
                form_kwargs={"request": self.request},
            )
            data["invoice_form"] = invoice_form
            data["formset"] = formset
            data["is_update"] = False
        return data

    def form_valid(self, form):
        print("calling form_valid in create")
        invoice_form = InvoiceForm(self.request.POST)
        formset = InvoiceLineFormSet(
            self.request.POST,
            form_kwargs={"request": self.request},
        )
        if invoice_form.is_valid() and formset.is_valid():
            invoice_form.instance.book = self.request.active_book
            invoice = invoice_form.save()
            formset.instance = invoice
            formset.save()
        else:
            return self.form_invalid
        return redirect("general_ledger:invoice-detail", pk=invoice.pk)
