import pytest
from rich import inspect

from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Invoice


class TestInvoiceFactory:
    @pytest.mark.django_db
    def test_create_invoice_simple_1(self):
        invoice = InvoiceFactory()
        # inspect(bank)
        assert isinstance(invoice, Invoice)

        invoices = InvoiceFactory.create_batch(
            10,
        )
