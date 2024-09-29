from formset.collection import FormCollection

from general_ledger.forms.formset.invoice_formsetified import (
    InvoiceFormFormsetified,
)
from general_ledger.forms.formset.invoice_line_collection import InvoiceLineCollection


class InvoiceCollection(FormCollection):

    invoice = InvoiceFormFormsetified()
    invoice_lines = InvoiceLineCollection()
    legend = "Invoices"
    add_label = "Add Invoice"
