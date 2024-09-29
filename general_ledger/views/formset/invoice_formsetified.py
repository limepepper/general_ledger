import logging
import sys

from formset.views import (
    EditCollectionView,
)
from loguru import logger

from general_ledger.forms.formset.invoice_collection import InvoiceCollection

from general_ledger.models import Invoice
from general_ledger.views.formset.formset_mixins import (
    CollectionViewMixin,
    SessionFormCollectionMixin,
)
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FormsetifyMixin,
)


"""
    renderer_args = [
        ('form_css_classes', kwargs.pop('form_classes', None)),
        ('fieldset_css_classes', kwargs.pop('fieldset_classes', None)),
        ('field_css_classes', kwargs.pop('field_classes', None)),
        ('label_css_classes', kwargs.pop('label_classes', None)),
        ('control_css_classes', kwargs.pop('control_classes', None)),
        ('form_css_classes', kwargs.pop('form_classes', None)),
        ('collection_css_classes', kwargs.pop('collection_classes', None)),
        ('max_options_per_line', kwargs.pop('max_options_per_line', None)),
    ]
"""


class InvoiceEditView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FormsetifyMixin,
    CollectionViewMixin,
    SessionFormCollectionMixin,
    EditCollectionView,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    model = Invoice
    collection_class = InvoiceCollection
    template_name = "gl/invoice/invoice-collection.html.j2"
    framework = "bootstrap"

    def __init__(self):
        super().__init__()
        self.active_book_id = None

    def get_form_collection(self):
        return super().get_form_collection()

    # def get_queryset(self):
    #     if not self.request.session.session_key:
    #         self.request.session.cycle_key()
    #     queryset = super().get_queryset()
    #     return queryset.filter(created_by=self.request.session.session_key)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        logger.debug(f"queryset model is {queryset.model}")

        if pk := self.kwargs.get(self.pk_url_kwarg):
            o = queryset.get(pk=pk)
            return o

        return self.model()
        # return None

    def get_collection_kwargs(self):
        kwargs = super().get_collection_kwargs()
        print(f"get_collection_kwargs {kwargs=}")
        return kwargs

    def get_extra_data(self):
        logger.debug(f"getting get_extra_data {self.kwargs=}")
        return super().get_extra_data()

    def get_initial(self):
        initial = super().get_initial()

        # initial["invoice"]["active_book_id"] = self.active_book_id
        if "invoice" in initial:
            initial["invoice"]["active_book_id"] = self.active_book_id
            if "invoice_lines" in initial:
                for item in initial["invoice_lines"]:
                    item["invoice_line"]["active_book_id"] = self.active_book_id
        initial["active_book_id"] = self.active_book_id
        return initial

    def get_context_data(self, **kwargs):
        logger.debug(f"getting get_context_data {kwargs=}")
        self.active_book_id = self.request.active_book.id
        context_data = super().get_context_data(**kwargs)
        context_data["active_book_id"] = self.active_book_id
        if self.object:
            context_data["change"] = True
        else:
            context_data["add"] = True
        return context_data
