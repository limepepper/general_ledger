import logging

from django.forms import (
    UUIDField,
    HiddenInput,
)
from django.forms import models

from general_ledger.models import Contact


class ContactInlineForm(
    models.ModelForm,
):

    logger = logging.getLogger(__name__)

    class Meta:
        model = Contact
        fields = [
            "name",
            "is_supplier",
            "is_customer",
            "is_vat_registered",
        ]

    id = UUIDField(
        required=False,
        widget=HiddenInput,
    )

    def get_context(self):
        context = super().get_context()
        context["click_actions"] = (
            "disable -> submit({add: true}) -> proceed !~ scrollToError"
        )
        return context

    extra_context = {
        "click_actions": "disable -> submit({add: true}) -> proceed !~ scrollToError",
        "click_actions_update": "disable -> submit({update: true}) -> proceed !~ scrollToError",
        "click_actions_delete": "disable -> submit({delete: true}) -> proceed !~ scrollToError",
        "button_css_classes": "mt-4",
    }
