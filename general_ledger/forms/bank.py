import logging

from django import forms
from django.db import transaction
from rich import inspect

from general_ledger.models import (
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
        exclude = ["book", "account", "slug", "id"]

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
        # inspect(self.instance, title=f"self.instance {self.instance._meta.model=}")

        # inspect(self.instance, title="self.instance1")

        # @TODO can just call is valid?
        bank_account = super().save(commit=False)

        # inspect(self.instance, title="self.instance2")

        # inspect(bank_account, title="bank_account")

        # is_new = not Bank.objects.filter(pk=self.instance.pk).exists()

        bank = Bank.objects.create_with_account(
            book=self.book,
            bank_id=self.instance.pk,
            **self.cleaned_data,
        )

        return bank
