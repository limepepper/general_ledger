import logging

from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
)
from django_filters.views import FilterView
from formset.views import IncompleteSelectResponseMixin, FormViewMixin

from general_ledger.filters import ContactFilter
from general_ledger.forms.contact import ContactUpdateForm
from general_ledger.models import Contact
from general_ledger.views.generic import GenericListView, GenericDetailView
from general_ledger.views.mixins import ActiveBookRequiredMixin, FormsetifyMixin
from general_ledger.views.mixins import GeneralLedgerSecurityMixIn

dLogger = logging.getLogger("form-debug")
dLogger.setLevel(logging.DEBUG)


class ContactListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    GenericListView,
):

    def get_queryset(self):
        return Contact.objects.for_book(self.request.active_book)

    model = Contact
    context_object_name = "contacts"
    paginate_by = 500
    filterset_class = ContactFilter

    def get_filterset(self, filterset_class):
        query_params = self.request.GET.copy()

        if hasattr(self, "kwargs"):
            query_params.update(self.kwargs)

        return filterset_class(query_params, queryset=self.get_queryset())


class ContactDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    GenericDetailView,
):
    model = Contact
    template_name = "gl/contact/contact_detail.html.j2"
    fields = [
        "name",
        "email",
        "phone",
        "address",
    ]


class ContactUpdateView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FormsetifyMixin,
    IncompleteSelectResponseMixin,
    FormViewMixin,
    UpdateView,
):
    logger = logging.getLogger("django.db.backends")

    dLogger.debug("ContactUpdateView : start")

    model = Contact
    template_name = "gl/contact/contact_form.html.j2"
    form_class = ContactUpdateForm
    success_url = reverse_lazy("general_ledger:contact-list")
    #
    # form = ContactUpdateForm()

    def get_context_data(self, **kwargs):
        dLogger.debug(
            f"ContactUpdateView : {'get_context_data' : >13} (start) kwargs: {kwargs}"
        )
        self.logger.info(f"ContactUpdateView : get_context_data kwargs: {kwargs}")
        context_data = super().get_context_data(**kwargs)
        if self.object:
            context_data["change"] = True
        else:
            context_data["add"] = True
        context_data["object_title"] = "Contact"
        context_data["request"] = self.request
        dLogger.debug(
            f"ContactUpdateView : get_context_data (returning) context_data: {context_data}"
        )
        return context_data

    def get_queryset(self):
        dLogger.debug("ContactUpdateView : get_queryset")
        qs = super().get_queryset()
        dLogger.debug("ContactUpdateView : get_queryset (returning)")
        return qs

    def get_object(self, queryset=None):
        dLogger.debug("ContactUpdateView : get_object (start)")
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        dLogger.debug("ContactUpdateView : get_object (returning)")
        if pk:
            return queryset.get(pk=pk)

    def get_form_kwargs(self):
        dLogger.debug("ContactUpdateView : get_form_kwargs")
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        dLogger.debug(f"ContactUpdateView : get_form_kwargs kwargs: {kwargs}")
        return kwargs

    def get(self, request, *args, **kwargs):
        dLogger.debug("ContactUpdateView : get (start)")
        self.logger.info(f"ContactUpdateView : get args {args} kwargs: {kwargs}")

        result = super().get(request, *args, **kwargs)
        dLogger.debug(f"ContactUpdateView : get (returning) {result}")
        return result

    def post(self, request, *args, **kwargs):
        dLogger.debug("ContactUpdateView : post")
        self.logger.info(f"ContactUpdateView : post args {args} kwargs: {kwargs}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        dLogger.debug("ContactUpdateView : form_valid")
        self.logger.info("calling form_valid in create")
        # active_book = self.request.session.get("active_book_pk")
        active_book = self.request.active_book
        self.logger.info(f"active_book: {active_book}")
        self.logger.info(f"form.instance.book: {form.instance}")
        form.instance.book = active_book
        if extra_data := self.get_extra_data():
            if extra_data.get("add") is True:
                form.instance.save()
                messages.info(self.request, "The instance was saved successfully")
                return JsonResponse({"success_url": self.get_success_url()})
            if extra_data.get("delete") is True:
                form.instance.delete()
                messages.warning(self.request, "The instance was deleted successfully")
                return JsonResponse({"success_url": self.get_success_url()})
        response = super().form_valid(form)
        messages.warning(self.request, "The instance was updated successfully")
        return response
