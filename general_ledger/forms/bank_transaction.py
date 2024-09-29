from django import forms

from general_ledger.models import BankStatementLine


class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankStatementLine
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
