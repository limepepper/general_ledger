import logging
from decimal import Decimal

from django.template.loader import get_template
from faker import Faker

from general_ledger.factories import LedgerFactory, ContactFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Invoice, Ledger, Contact, InvoiceLine, TaxRate
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


class TestInvoiceStuff1(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_no_vat_invoice(self):

        ledger = LedgerFactory()
        invoice = Invoice.objects.create(
            ledger=ledger,
            contact=ContactFactory.customer(book=ledger.book),
            invoice_number="INV-001",
            date="2024-01-01",
            due_date="2024-01-31",
            tax_inclusive=TaxInclusive.NONE,
        )
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description="line 1",
            vat_rate=TaxRate.objects.get(slug="20-vat-on-income", book=ledger.book),
            quantity=1,
            unit_price=40.0000,
        )

        self.assertEqual(invoice.total_amount, Decimal(40))
        self.assertEqual(invoice.total_inclusive(), Decimal(40))
        self.assertEqual(invoice.total_tax(), Decimal(0))
        self.assertEqual(invoice.subtotal(), Decimal(40))

        invoice_line2 = InvoiceLine.objects.create(
            invoice=invoice,
            description="line 2",
            vat_rate=TaxRate.objects.get(slug="5-vat-on-income", book=ledger.book),
            quantity=1,
            unit_price=40.0000,
        )

        self.assertEqual(invoice.total_amount, Decimal(80))
        self.assertEqual(invoice.total_inclusive(), Decimal(80))
        self.assertEqual(invoice.total_tax(), Decimal(0))
        self.assertEqual(invoice.subtotal(), Decimal(80))
