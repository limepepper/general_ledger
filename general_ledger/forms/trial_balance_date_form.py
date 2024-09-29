# forms.py
from django import forms


class TrialBalanceDateForm(forms.Form):
    name = forms.DateField()
