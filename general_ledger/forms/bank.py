import logging

from django import forms
from django.forms import (
    UUIDField,
    HiddenInput,
)
from formset.widgets import Selectize
from django.forms import models
from django.db import transaction
from general_ledger.models import (
    Bank,
    Account,
    TaxRate,
    AccountType,
)


class BankForm(
    # FormMixin,
    forms.ModelForm,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    class Meta:
        model = Bank
        fields = "__all__"
        exclude = ["book"]

    def __init__(self, *args, **kwargs):
        self.logger.debug(f"BankForm kwargs: {args} {kwargs}")
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.logger.debug(f"BankForm kwargs2: {kwargs}")
        # self.fields["book"].value = "off"

        if request and hasattr(request, "active_book"):
            self.book = request.active_book
        else:
            raise ValueError("No book found")

        self.fields["id"].queryset = Account.objects.for_book(self.book)

    id = models.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=Selectize(
            search_lookup="name__icontains",
        ),
        required=False,
    )

    @transaction.atomic
    def save(self, commit=True):
        # First, create the Account instance
        account = Account.objects.create(
            name=self.cleaned_data["name"],
            coa=self.book.get_default_coa(),
            tax_rate=TaxRate.objects.get(
                slug="no-vat",
                book=self.book,
            ),
            type=AccountType.objects.get(
                name="Bank",
                book=self.book,
            ),
        )

        # Now, create the BankAccount instance
        bank_account = super().save(commit=False)
        bank_account.id = account

        if commit:
            bank_account.save()

        return bank_account
