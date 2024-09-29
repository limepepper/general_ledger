import logging

from django import forms

from general_ledger.models import InvoiceLine, TaxRate


class InvoiceLineForm(forms.ModelForm):
    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    template_name_table = "gl/forms/table.html"
    # template_name_table = "django2/forms/table.html"

    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-number",
                "placeholder": "Quantity",
                "maxlength": 8,
            }
        ),
    )

    unit_price = forms.DecimalField(
        max_digits=8,
        decimal_places=4,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-number",
                "placeholder": "Unit Price",
                "maxlength": 8,
            }
        ),
    )

    class Meta:
        model = InvoiceLine
        fields = [
            "description",
            "quantity",
            "unit_price",
            "vat_rate",
        ]
        widgets = {
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description",
                }
            ),
            "vat_rate": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            # "vat_rate": forms.ModelChoiceField(queryset=Account.objects.filter(book=author))
            # "vat_rate": VatRateWidget,
        }
        labels = {
            "description": False,
            "quantity": False,
            "unit_price": False,
            "vat_rate": False,
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        # self.logger.debug(f"InvoiceLineForm __init__ request: {request}")
        super().__init__(*args, **kwargs)

        if request and hasattr(request, "active_book"):
            self.fields["vat_rate"].queryset = TaxRate.objects.filter(
                book=request.active_book
            )
        else:
            self.fields["vat_rate"].queryset = TaxRate.objects.none()
