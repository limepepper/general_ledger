import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.template.loader import get_template
from faker import Faker
from rich import inspect

from general_ledger.factories import LedgerFactory, ContactFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Invoice, Ledger, Contact, InvoiceLine, TaxRate
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


class TestInvoiceWorkflowConstraints(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_invoice_cant_be_edited_non_draft(self):

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

        self.assertTrue(invoice.can_record())
        invoice.do_next()

        self.assertTrue(invoice.is_awaiting_approval())

        with self.assertRaises(ValidationError) as context:

            invoice_line3 = InvoiceLine.objects.create(
                invoice=invoice,
                description="line 3",
                vat_rate=TaxRate.objects.get(slug="5-vat-on-income", book=ledger.book),
                quantity=1,
                unit_price=40.0000,
            )

        self.assertTrue(invoice.is_awaiting_approval())

        with self.assertRaises(ValidationError) as context:

            invoice_line2.unit_price = 50.0000
            invoice_line2.save()

        with self.assertRaises(ValidationError) as context:
            invoice.invoice_lines.first().delete()

        with self.assertRaises(ValidationError) as context:
            invoice_line2.delete()

        with self.assertRaises(ValidationError) as context:
            invoice.delete()

        with self.assertRaises(ValidationError) as context:
            invoice_fresh = Invoice.objects.get(pk=invoice.pk)
            invoice_fresh.delete()

    def test_customer_contact_constraint(self):
        ledger = LedgerFactory()
        contact = ContactFactory.supplier(
            book=ledger.book,
            is_customer=False,
        )
        inspect(contact)
        invoice = Invoice.objects.create(
            ledger=ledger,
            contact=contact,
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
        inspect(invoice)

        with self.assertRaises(ValidationError) as _:
            invoice.full_clean()

        self.assertFalse(invoice.is_valid)
