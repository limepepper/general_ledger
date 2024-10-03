import logging

from django.forms import (
    UUIDField,
    HiddenInput,
)
from django.forms import models
from formset.widgets import Selectize

from general_ledger.models import Contact, Account, TaxRate


class ContactUpdateForm(
    models.ModelForm,
):

    logger = logging.getLogger(__name__)
    logger.debug("ContactUpdateForm : start")

    class Meta:
        model = Contact
        fields = "__all__"
        exclude = ["book"]

    id = UUIDField(
        required=False,
        widget=HiddenInput,
    )

    sales_account = models.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=Selectize(
            search_lookup="name__icontains",
            # filter_by={"coa": "coa_id"},
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.logger.debug("ContactUpdateForm : __init__")
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if "instance" in kwargs and kwargs["instance"]:
            book = kwargs["instance"].book
        elif request and hasattr(request, "active_book"):
            book = request.active_book
        else:
            raise ValueError("No book found")

        self.fields["sales_account"].queryset = Account.objects.for_book(book)
        self.fields["sales_tax_rate"].queryset = TaxRate.objects.filter(book=book)
        self.fields["purchases_account"].queryset = Account.objects.for_book(book)
        self.fields["purchases_tax_rate"].queryset = TaxRate.objects.filter(book=book)
