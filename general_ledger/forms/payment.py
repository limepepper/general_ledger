import logging

from django import forms
from django_select2.forms import ModelSelect2Widget

from general_ledger.models import (
    TaxRate,
    Account,
    Contact,
)

from django.forms import (
    UUIDField,
    HiddenInput,
)


class PaymentCreateForm(forms.Form):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.active_book_id = kwargs.pop("active_book_id", None)
        super().__init__(*args, **kwargs)

    def is_valid(self):
        is_valid = super().is_valid()
        print(f"{is_valid=}")
        return is_valid

    def save(self):
        bank_statement_line = self.cleaned_data.pop("bank_statement_line")
        # pb = PaymentBuilder(
        #     bank_statement_line=bank_statement_line,
        #     active_book_id=self.active_book_id,
        # )

    def get_context(self):
        # print(f"PaymentCreateForm qs {self.fields['contact'].queryset}")

        self.fields["contact"].queryset = Contact.objects.for_book(
            self.active_book_id
        ).customers()
        self.fields["account"].queryset = Account.objects.for_book(self.active_book_id)
        self.fields["vat_rate"].queryset = TaxRate.objects.for_book(self.active_book_id)
        self.fields["bank_statement_line"].initial = self.instance.id
        context = super().get_context()
        return context

    # sales_account = models.ModelChoiceField(
    #     queryset=Account.objects.all(),
    #     widget=Selectize(
    #         search_lookup="name__icontains",
    #         # filter_by={"coa": "coa_id"},
    #     ),
    #     required=False,
    # )
    bank_statement_line = forms.UUIDField(
        required=False,
        widget=HiddenInput,
    )

    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        required=True,
        widget=ModelSelect2Widget(
            search_fields=["name__icontains"],
        ),
        label=False,
    )
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=True,
        widget=ModelSelect2Widget(
            search_fields=["name__icontains"],
        ),
        label=False,
    )
    description = forms.CharField()
    vat_rate = forms.ModelChoiceField(
        queryset=TaxRate.objects.all(),
        required=True,
        label=False,
    )

    class Meta:
        fields = "__all__"
        labels = {
            "contact": False,
            "account": False,
            "vat_rate": False,
        }
