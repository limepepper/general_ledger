from django.forms import (
    ModelForm,
    UUIDField,
    HiddenInput,
    TextInput,
    IntegerField,
    NumberInput,
)
from django.forms.fields import CharField
from formset.utils import FormMixin
from loguru import logger

from general_ledger.models import (
    InvoiceLine,
    TaxRate,
)


class InvoiceLineForm(
    FormMixin,
    ModelForm,
):

    class Meta:
        model = InvoiceLine
        fields = [
            "id",
            "description",
            "unit_price",
            "quantity",
            "vat_rate",
        ]
        widgets = {
            "description": TextInput(
                attrs={},
            ),
        }

    id = UUIDField(
        required=False,
        widget=HiddenInput,
    )

    quantity = IntegerField(
        widget=NumberInput(
            attrs={
                "class": "form-control form-number",
                "placeholder": "Quantity1",
                "maxlength": 8,
            }
        ),
    )

    name = CharField(
        max_length=40,
        required=False,
        widget=HiddenInput(),
        initial="",
    )

    def get_initial_for_field(self, field, field_name):
        logger.debug(f"InvoiceLineForm : get_initial_for_field {field=}")
        result = super().get_initial_for_field(field, field_name)
        logger.debug(f"InvoiceLineForm : get_initial_for_field {result=}")
        return result

    def get_context(self):
        logger.debug(f"InvoiceLineForm : get_context {self.instance=}")

        self.fields["vat_rate"].queryset = TaxRate.objects.filter(
            book_id=self.active_book_id
        )

        context = super().get_context()
        return context

    # default_renderer = FormRenderer(
    #     form_css_classes="row",
    #     # label_css_classes="something",
    #     # control_css_classes="here",
    #     field_css_classes={
    #         "*": "mb-2 col-2",
    #         "description": "col-2",
    #         "unit_price": "col-2",
    #         "invoice_number": "col-3",
    #         "vat_rate": "col-3",
    #         "date": "col-3",
    #         "due_date": "col-3",
    #         "tax_inclusive": "col-3",
    #         "submit": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
    #         "reset": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
    #     },
    # )

    # unit_price = forms.DecimalField(
    #     max_digits=8,
    #     decimal_places=2,
    #     widget=forms.NumberInput(
    #         attrs={
    #             "class": "form-control form-number",
    #             "placeholder": "Unit Price",
    #             "maxlength": 8,
    #         }
    #     ),
    # )
