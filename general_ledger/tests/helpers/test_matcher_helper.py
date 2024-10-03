from django.test import RequestFactory, TestCase
from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from rich import inspect

from general_ledger.builders.invoice_builder import InvoiceBuilder
from general_ledger.factories import BookFactory, ContactFactory, BankAccountFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.helpers.matcher import MatcherHelper
from general_ledger.models import Bank
from general_ledger.models.bank_statement_line_type import BankStatementLineType


@pytest.fixture()
def resources():
    print("setup")
    book = BookFactory()
    bank = BankAccountFactory(book=book)
    yield book, bank
    print("teardown")


class TestMatcherHelper:
    @pytest.mark.django_db
    def test_exact_one_to_one_match(self, resources):
        book, bank = resources
        invoice = (
            InvoiceBuilder(
                ledger=book.get_default_ledger(),
            )
            .add_memo_invoice(
                amount=100,
                date=(datetime.now() - timedelta(days=40)).date(),
                due_date=(datetime.now() - timedelta(days=30)).date(),
                sales_account__slug="sales",
                tax_rate__slug="no-vat",
                contact=ContactFactory.customer(book=book),
                description="Simple invoice",
            )
            .build()
        )
        assert invoice is not None and invoice.amount == 100
        invoice.do_next()
        invoice.do_next()
        assert all(
            [
                invoice is not None,
                invoice.amount == 100,
                invoice.is_overdue,
                invoice.is_awaiting_payment(),
                invoice.transactions.count() == 1,
            ]
        )

        tx = BankTransactionFactory(
            bank=bank,
            date=(datetime.now() - timedelta(days=20)).date(),
            amount=100,
            type=BankStatementLineType.CREDIT,
        )
        matcher = MatcherHelper()
        matcher.reconcile_bank_statement()
        assert len(matcher.candidates["exact"]) == 1

    @pytest.mark.django_db
    def test_combo_matcher(self, resources):
        """
        Test that the combo matcher can match two invoices to a single bank transaction
        :param resources:
        :return:
        """
        book, bank = resources
        invoice1 = (
            InvoiceBuilder(
                ledger=book.get_default_ledger(),
            )
            .add_memo_invoice(
                amount=50,
                date=(datetime.now() - timedelta(days=40)).date(),
                due_date=(datetime.now() - timedelta(days=30)).date(),
                sales_account__slug="sales",
                tax_rate__slug="no-vat",
                contact=ContactFactory.customer(book=book),
                description="Simple invoice 1",
            )
            .build()
        )
        invoice2 = (
            InvoiceBuilder(
                ledger=book.get_default_ledger(),
            )
            .add_memo_invoice(
                amount=50,
                date=(datetime.now() - timedelta(days=40)).date(),
                due_date=(datetime.now() - timedelta(days=30)).date(),
                sales_account__slug="sales",
                tax_rate__slug="no-vat",
                contact=ContactFactory.customer(book=book),
                description="Simple invoice 2",
            )
            .build()
        )
        for invoice in [invoice1, invoice2]:
            assert invoice is not None and invoice.amount == 50
            invoice.do_next()
            invoice.do_next()
            assert all(
                [
                    invoice is not None,
                    invoice.amount == 50,
                    invoice.is_overdue,
                    invoice.is_awaiting_payment(),
                    invoice.transactions.count() == 1,
                ]
            )

        tx = BankTransactionFactory(
            bank=bank,
            date=(datetime.now() - timedelta(days=20)).date(),
            amount=100,
            type=BankStatementLineType.CREDIT,
        )
        matcher = MatcherHelper()
        matcher.reconcile_bank_statement()
        inspect(matcher.candidates)
        assert len(matcher.candidates["combination"]) == 1

    @pytest.mark.django_db
    def test_xfer_matcher(self, resources):
        book, bank = resources

        bank_1 = BankAccountFactory(type=Bank.CHECKING)
        bank_2 = BankAccountFactory(type=Bank.SAVINGS)

        num_transfers = 10

        txs = BankTransactionFactory.create_transfers(
            [bank_1, bank_2],
            num_transfers,
        )
        assert len(txs) == 2 * num_transfers
        matcher = MatcherHelper()
        matcher.reconcile_bank_statement()
        # inspect(matcher.candidates)
        assert len(matcher.candidates["transfer"]) == num_transfers

        # this shouldn't change anything
        matcher.reconcile_bank_statement()
        assert len(matcher.candidates["transfer"]) == num_transfers
