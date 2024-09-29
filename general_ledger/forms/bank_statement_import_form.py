from django import forms


class BankStatementImportForm(forms.Form):
    import_file = forms.FileField()
