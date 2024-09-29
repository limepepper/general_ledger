import logging

from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView
from django_filters.views import FilterView
from formset.views import FormViewMixin

from general_ledger.forms.bank import BankForm
from general_ledger.models import Bank, BankStatementLine
from general_ledger.views.generic import GenericListView
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class BankListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    GenericListView,
):

    model = Bank
    context_object_name = "banks"
    # filterset_class = BankFilter

    def get_context_data(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.error("BankListView : get_context_data")
        context_data = super().get_context_data(**kwargs)
        return context_data


class BankDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    DetailView,
):
    model = Bank
    template_name = "gl/bank/bank_detail.html.j2"
    context_object_name = "bank"


class BankUpdateView(
    SuccessMessageMixin,
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    # IncompleteSelectResponseMixin,
    FormViewMixin,
    UpdateView,
):

    logger = logging.getLogger(__name__)

    success_message = "%(name)s was updated successfully"

    model = Bank
    template_name = "gl/bank/bank_form.html.j2"
    form_class = BankForm
    success_url = reverse_lazy("general_ledger:bank-list")

    extra_context = {
        "click_actions": "disable -> submit({add: true}) -> proceed !~ scrollToError",
        "click_actions_update": "disable -> submit({update: true}) -> proceed !~ scrollToError",
        "click_actions_delete": "disable -> submit({delete: true}) -> proceed !~ scrollToError",
        "button_css_classes": "mt-4",
    }

    def get_form_kwargs(self):
        # dLogger.debug("ContactUpdateView : get_form_kwargs")
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        # dLogger.debug(f"ContactUpdateView : get_form_kwargs kwargs: {kwargs}")
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.object:
            context_data["change"] = True
        else:
            context_data["add"] = True
        context_data["object_title"] = "Bank"
        return context_data

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            return queryset.get(pk=pk)

    def form_valid(self, form):
        # print("calling form_valid in create")
        # active_book = self.request.session.get("active_book_pk")
        active_book = self.request.active_book
        self.logger.error(f"active_book: {active_book}")
        self.logger.error(f"form.instance.book: {form.instance}")
        form.instance.book = active_book
        if extra_data := self.get_extra_data():
            # if extra_data.get("add") is True:
            #     form.instance.save()
            #     return JsonResponse({"success_url": self.get_success_url()})
            if extra_data.get("delete") is True:
                form.instance.delete()
                return JsonResponse({"success_url": self.get_success_url()})
        return super().form_valid(form)
