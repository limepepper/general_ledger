from general_ledger.factories import LedgerFactory, ContactFactory
from general_ledger.models import PurchaseInvoice, InvoiceLine
from general_ledger.models.invoice_purchaseinvoice_line import PurchaseInvoiceLine
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


class TestPurchaseInvoiceSimple1(GeneralLedgerBaseTest):
    def test_purchase_invoice(self):

        ledger = LedgerFactory()
        invoice = PurchaseInvoice.objects.create(
            ledger=ledger,
            contact=ContactFactory.supplier(
                book=ledger.book,
            ),
            invoice_number="BILL-001",
            date="2024-01-01",
            due_date="2024-01-31",
            tax_inclusive=TaxInclusive.EXCLUSIVE,
        )

        self.assertEqual(invoice.tax_inclusive, TaxInclusive.EXCLUSIVE)

        invoice_line = PurchaseInvoiceLine.objects.create(
            invoice=invoice,
            description="Test",
            quantity=1,
            unit_price=100,
            vat_rate=invoice.ledger.book.taxrate_set.get(slug="no-vat"),
        )
