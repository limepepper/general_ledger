# import logging
from decimal import Decimal

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
        ib1 = InvoiceBuilder(
            ledger=book.get_default_ledger(),
        )
        ib1.add_memo_invoice(
            amount=100,
            description="Simple invoice using memo",
            date=(datetime.now() - timedelta(days=40)).date(),
            due_date=(datetime.now() - timedelta(days=30)).date(),
            contact=contact,
        )
        invoice = ib1.build()
        assert invoice.is_valid
        #inspect(invoice)

        ib2 = InvoiceBuilder(
            ledger=book.get_default_ledger(),
            description="Simple invoice",
            contact=ContactFactory.customer(book=book),
            date=(datetime.now() - timedelta(days=40)).date(),
            due_date=(datetime.now() - timedelta(days=30)).date(),
        )
        ib2.add_line(
            description="A simple line item",
            unit_price=Decimal("100.0000"),
        )
        invoice2 = ib2.build()
        assert invoice2.is_valid
        invoice2.do_posted()
        assert invoice2.is_valid
        # inspect(invoice2)

