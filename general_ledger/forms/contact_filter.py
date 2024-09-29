from django import forms

from general_ledger.models import Contact


class ContactFilterForm(forms.ModelForm):
    is_customer = forms.BooleanField(required=False)
    is_supplier = forms.BooleanField(required=False)

    class Meta:
        model = Contact
