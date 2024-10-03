from django import forms
from rich import inspect

from general_ledger.models import (
    Payment,
)


class PaymentEditForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "is_posted",
        ]

    def is_valid(self):
        return super().is_valid()

    def save(self, commit=True):
        # inspect(self.instance)
        if "promote" in self.data:
            self.instance.promote()
        elif "demote" in self.data:
            self.instance.demote()
        return self.instance
