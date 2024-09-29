from django import forms
from import_export import resources, fields
from import_export.forms import ImportForm, ConfirmImportForm

from general_ledger.models import Ledger, Transaction

import logging


class TransactionLedgerImportForm(ImportForm):
    """
    Form for importing transactions with embedded ledger selection.
    """

    def __init__(self, import_formats, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("in TransactionLedgerImportForm.__init__")
        super(TransactionLedgerImportForm, self).__init__(
            import_formats, *args, **kwargs
        )

    ledger = forms.ModelChoiceField(
        queryset=Ledger.objects.all(),
        required=True,
        help_text="Select the ledger to which these transactions will belong.",
    )


class TransactionLedgerConfirmImportForm(ConfirmImportForm):
    ledger = forms.CharField(widget=forms.HiddenInput())
