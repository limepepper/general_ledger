# import logging
import pytest
from rich import inspect

from general_ledger.builders.invoice_builder import InvoiceBuilder
from general_ledger.factories import BookFactory, ContactFactory
from datetime import datetime, timedelta

class TestInvoiceBuilder():

    @pytest.mark.django_db
    def test_invoice_builder_memo_invoice(self):
        book = BookFactory()
        contact = ContactFactory.customer(book=book)
        ib = InvoiceBuilder(
            ledger=book.get_default_ledger(),
        )
        ib.add_memo_invoice(
            amount=100,
            description="Simple invoice using memo",
            date=(datetime.now() - timedelta(days=40)).date(),
            due_date=(datetime.now() - timedelta(days=30)).date(),
            contact=contact,
        )
        invoice = ib.build()
        inspect(invoice)
