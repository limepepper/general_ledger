import django
from django.forms import (
    ModelForm,
    UUIDField,
    HiddenInput,
)
from django.forms import models
from django.forms.models import model_to_dict
from formset.renderers.bootstrap import FormRenderer
from formset.utils import FormMixin
from loguru import logger

from general_ledger.models import (
    Invoice,
    Contact,
    Ledger,
)
from general_ledger.widgets import InvoiceContactModelChoiceWidget


class InvoiceFormFormsetified(
    FormMixin,
    ModelForm,
):

    class Meta:
        model = Invoice
        fields = [
            "id",
            "contact",
            "ledger",
            "description",
            "invoice_number",
            "date",
            "due_date",
            "tax_inclusive",
        ]
        widgets = {
            "date": django.forms.DateInput(
                attrs={"type": "date"},
            ),
            "due_date": django.forms.DateInput(
                attrs={"type": "date"},
            ),
        }

    id = UUIDField(
        required=False,
        widget=HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        logger.trace("InvoiceFormFormsetified : __init__ {kwargs=}")
        request = kwargs.pop("request", None)
        logger.trace(f"kwargs: {kwargs}   request: {request}")
        super().__init__(*args, **kwargs)

    def get_context(self):
        logger.trace(f"InvoiceFormFormsetified qs {self.fields['contact'].queryset}")

        self.fields["contact"].queryset = Contact.objects.for_book(
            self.initial["active_book_id"]
        ).customers()
        self.fields["ledger"].queryset = Ledger.objects.for_book(
            self.initial["active_book_id"]
        )
        context = super().get_context()
        return context

    def model_to_dict(self, instance):
        opts = self._meta
        # active_book = instance.pop("active_book_id")
        result = model_to_dict(instance, opts.fields, opts.exclude)
        logger.trace(f"model_to_dict {result=}")
        result["book_id"] = "123"
        return result

    default_renderer = FormRenderer(
        form_css_classes="row",
        # label_css_classes="something",
        # control_css_classes="here",
        field_css_classes={
            "*": "mb-2 col-2",
            "contact": "col-3",
            "ledger": "col-3",
            "invoice_number": "col-3",
            "description": "col-3",
            "date": "col-3",
            "due_date": "col-3",
            "tax_inclusive": "col-3",
            "submit": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
            "reset": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
        },
    )

    # date = DateField(
    #     widget=DateInput(attrs={"type": "date"}),
    #     initial=datetime.date.today,
    # )

    contact = models.ModelChoiceField(
        queryset=Contact.objects.all(),
        # widget=Selectize(
        #     search_lookup="name__icontains",
        #     # filter_by={"coa": "coa_id"},
        # ),
        widget=InvoiceContactModelChoiceWidget(),
        required=True,
    )

    # def __init__(self, *args, **kwargs):
    #     dLogger.debug("InvoiceForm : __init__")
    #     request = kwargs.pop("request", None)
    #     super().__init__(*args, **kwargs)
    #
    #     if "instance" in kwargs and kwargs["instance"]:
    #         book = kwargs["instance"].ledger.book
    #     elif request and hasattr(request, "active_book"):
    #         book = request.active_book
    #     else:
    #         raise ValueError("No book found")
    #
    #     self.fields["ledger"].queryset = Ledger.objects.for_book(book)
    #     self.fields["contact"].queryset = Contact.objects.for_book(book)
