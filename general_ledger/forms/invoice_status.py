from django.forms import ModelForm

from general_ledger.models import Invoice


class InvoiceStatusForm(ModelForm):
    class Meta:
        model = Invoice
        fields = ("status",)
        # exclude = ["book"]

    def save(self, commit=True):
        print(f"InvoiceStatusForm save {self.cleaned_data}")
        invoice = super().save(commit=False)

        if commit:
            invoice.save()
        return invoice
