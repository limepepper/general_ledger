# import logging
from datetime import date
from decimal import Decimal

from django.test import override_settings
from loguru import logger

from general_ledger.builders.invoice import InvoiceBuilder
from general_ledger.builders.payment import PaymentBuilder
from general_ledger.factories import ContactFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.models import (
    Book,
    Bank,
    Invoice,
)
from general_ledger.tests import GeneralLedgerBaseTest


# Create your tests here.
class TestPaymentBuilder(GeneralLedgerBaseTest):

    # logger = logging.getLogger(__name__)

    @override_settings(DEBUG=True)
    def test_simple(self):
        self.logger.debug("Test simple")
        self.assertEqual(1, 1)

        book = Book.objects.first()
        book.initialize()
        ledger = book.get_default_ledger()
        bank = Bank.objects.for_book(book).first()

        logger.info(f"{book=} {ledger=} {bank=}")

        bank_statement_line = BankTransactionFactory(
            bank=bank,
            amount=Decimal(100.0000),
        )

        ib = InvoiceBuilder(
            ledger=ledger,
            description="Simple invoice",
            contact=ContactFactory.customer(book=book),
        )
        ib.add_line(
            contact=ContactFactory.customer(book=book),
            description="A simple line item",
            unit_price=Decimal(100.0000),
            sales_account__slug="sales",
            tax_rate__slug="no-vat",
        )

        logger.info(f"calling build on the invoice builder")
        invoice = ib.build()
        invoice.do_next()

        # inspect(invoice)
        # inspect(invoice.invoice_lines.all())
        # inspect(invoice.transactions.all())
        assert invoice.transactions.count() == 1

        invoice.do_next()

        assert invoice.amount == Decimal(100.0000)

        assert (
            Invoice.InvoiceStatus(invoice.status)
            == Invoice.InvoiceStatus.AWAITING_PAYMENT
        )

        pb = PaymentBuilder(
            description="Simple Receive money payment",
            ledger=ledger,
            date=date.today(),
        )

        pb.add_item(
            from_object=bank_statement_line,
            to_object=invoice,
        )

        payment = pb.build()

        payment.to_state_recorded()

        assert payment.amount == Decimal(100.0000)

        assert invoice.transactions.count() == 1
        assert payment.transactions.count() == 1
        assert invoice.transactions.first().entry_set.count() == 3
        assert payment.transactions.first().entry_set.count() == 2

        @override_settings(DEBUG=True)
        def test_memo_payment(self):
            pass

        # pb.add_memo_payment(
        #     contact=ContactFactory.customer(book=book),
        #     amount=Decimal(100.0000),
        #     # @TODO this dumb
        #     sales_account__slug="sales",
        #     tax_rate__slug="no-vat",
        #     bank_statement_line=bank_transaction,
        # )
        #
        # payment = pb.build()

        # self.assertTrue(payment.invoice.amount == Decimal(100.0000))
