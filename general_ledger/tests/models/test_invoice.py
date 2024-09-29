import logging
from decimal import Decimal

from django.template.loader import get_template
from faker import Faker

from general_ledger.factories import LedgerFactory, ContactFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Invoice, Ledger, Contact, InvoiceLine, TaxRate
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


# this is to test creating invoice lines
class TestInvoice(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_stuff1(self):
        """
        test vanilla instances can be created
        """
        ledger = LedgerFactory()
        invoice = Invoice.objects.create(
            ledger=ledger,
            contact=ContactFactory.customer(book=ledger.book),
            invoice_number="INV-001",
            date="2024-01-01",
            due_date="2024-01-31",
            tax_inclusive=TaxInclusive.EXCLUSIVE,
        )
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description="line 1",
            vat_rate=TaxRate.objects.get(slug="20-vat-on-income", book=ledger.book),
            quantity=1,
            unit_price=40.0000,
        )
        invoice_line2 = InvoiceLine.objects.create(
            invoice=invoice,
            description="line 2",
            vat_rate=TaxRate.objects.get(slug="5-vat-on-income", book=ledger.book),
            quantity=10,
            unit_price=385.2500,
        )
        invoice_line3 = InvoiceLine.objects.create(
            invoice=invoice,
            description="line 3",
            vat_rate=TaxRate.objects.get(slug="5-vat-on-income", book=ledger.book),
            quantity=5,
            unit_price=430.2500,
        )

        template = get_template("gl/console/invoice-header.j2")
        print(template.render(context={"invoice": invoice}))
        template = get_template("gl/console/invoice-lines.j2")
        print(template.render(context={"invoice": invoice}))

        # inspect(invoice)
        print(f"{invoice.tax_inclusive=}")
        print(f"invoice_line: {invoice_line}")
        print(f"line_total_exclusive: {invoice_line.line_total_exclusive()}")
        print(f"invoice_line tax_amount: {invoice_line.tax_amount()}")
        print(f"invoice subtotal: {invoice.subtotal()}")
        print(f"invoice.total_inclusive: {invoice.total_inclusive()}")

    def test_tax_exclusive(self):
        invoice = InvoiceFactory(
            create_invoice_lines=[],
            tax_inclusive=TaxInclusive.EXCLUSIVE,
        )
        invoice.save()
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description="Test",
            quantity=1,
            unit_price=100,
            vat_rate=invoice.get_sales_vat_rate(),
        )
        self.assertEqual(invoice.invoice_lines.count(), 1)
        self.assertEqual(invoice.total_amount, 120)
        self.assertEqual(invoice.total_tax(), 20)
        self.assertEqual(invoice.subtotal(), 100)

    def test_tax_inclusive(self):
        invoice = InvoiceFactory(
            create_invoice_lines=[],
            tax_inclusive=TaxInclusive.INCLUSIVE,
        )
        invoice.save()
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description="Test",
            quantity=1,
            unit_price=100,
            vat_rate=invoice.get_sales_vat_rate(),
        )
        self.assertEqual(invoice.invoice_lines.count(), 1)
        self.assertEqual(invoice.total_amount, 100)
        self.assertEqual(
            invoice.total_tax(),
            Decimal(100.000)
            * (
                invoice.get_sales_vat_rate().rate
                / (Decimal(1.0) + invoice.get_sales_vat_rate().rate)
            ),
        )
        self.assertEqual(
            invoice.subtotal(),
            Decimal(100.000)
            * (
                Decimal(1.0)
                - (
                    (invoice.get_sales_vat_rate().rate)
                    / (Decimal(1.0) + invoice.get_sales_vat_rate().rate)
                )
            ),
        )
