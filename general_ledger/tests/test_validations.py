import logging

from rich import inspect

from general_ledger.factories import LedgerFactory, ContactFactory
from general_ledger.django.models import Invoice
from general_ledger.django.models.tax_inclusive import TaxInclusive
from general_ledger.tests import GeneralLedgerBaseTest


class TestValidations(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_validation_mixin(self):

        ledger = LedgerFactory()
        invoice = Invoice(
            ledger=ledger,
            contact=ContactFactory.customer(
                book=ledger.book,
            ),
            invoice_number="INV-001",
            date="2024-01-01",
            due_date="2024-01-31",
            tax_inclusive=TaxInclusive.NONE,
        )

        assert invoice.is_valid
        assert invoice.is_overdue is False

        invoice.save()

        invoice.refresh_from_db()
