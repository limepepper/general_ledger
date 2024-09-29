from decimal import Decimal

from rich import inspect

from general_ledger.factories.invoice import InvoiceFactory, InvoiceLineFactory
from general_ledger.models import InvoiceLine
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


class TestInvoiceLine(GeneralLedgerBaseTest):
    def test_no_tax_independent_of_invoice_tax_inclusive_setting(self):
        invoice = InvoiceFactory(
            create_invoice_lines=[],
            tax_inclusive=TaxInclusive.EXCLUSIVE,
        )
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description="Test",
            quantity=1,
            unit_price=100,
            vat_rate=invoice.ledger.book.taxrate_set.get(slug="no-vat"),
        )

        self.assertEqual(invoice.total_amount, 100)
        self.assertEqual(invoice.total_tax(), 0)
        self.assertEqual(invoice.subtotal(), 100)

        invoice.tax_inclusive = TaxInclusive.INCLUSIVE
        invoice.save()

        self.assertEqual(invoice.total_amount, 100)
        self.assertEqual(invoice.total_tax(), 0)
        self.assertEqual(invoice.subtotal(), 100)

        invoice.tax_inclusive = TaxInclusive.NONE
        invoice.save()

        self.assertEqual(invoice.total_amount, 100)
        self.assertEqual(invoice.total_tax(), 0)
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
