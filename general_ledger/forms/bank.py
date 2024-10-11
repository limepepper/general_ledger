import logging

from django import forms
from django.db import transaction
from rich import inspect

from general_ledger.django.models import (
    Bank,
)


class BankForm(
    # FormMixin,
    forms.ModelForm,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    class Meta:
        model = Bank
        fields = "__all__"
        exclude = ["book", "account", "slug", "id", "tz"]

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

    @transaction.atomic
    def save(self, commit=True):
        if not commit:
            raise ValueError("Cannot save without commit=True")

        # @TODO can just call is valid?
        bank_account = super().save(commit=False)

        # is_new = not Bank.objects.filter(pk=self.instance.pk).exists()

        bank = Bank.objects.create_with_account(
            book=self.book,
            bank_id=self.instance.pk,
            **self.cleaned_data,
        )

        return bank
