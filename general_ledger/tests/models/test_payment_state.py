from django.test import TestCase
from uuid import uuid4, UUID


import logging

from rich import inspect

from general_ledger.factories import BookFactory, BankAccountFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Book, Ledger, Payment, Bank
from general_ledger.models.document_status import DocumentStatus
from general_ledger.tests import GeneralLedgerBaseTest


# Create your tests here.
class PaymentStateTests(GeneralLedgerBaseTest):

    def test_payment_state(self):

        # inspect(Book.objects.all())

        book = Book.objects.first()
        # inspect(book)
        ledger = book.get_default_ledger()
        bank = Bank.objects.filter(type=Bank.CHECKING, book=book).first()
        tx = BankTransactionFactory(
            bank=bank,
            amount=100,
        )
        invoice = InvoiceFactory(
            ledger=ledger,
        )
        # inspect(invoice)
        for il in invoice.invoice_lines.all():
            inspect(il)

        print(invoice.full_clean())

        payment = Payment.objects.create(
            date="2022-01-01",
            ledger=ledger,
        )

        payment.items.create(
            amount=100,
            from_object=tx,
            from_account=tx.bank.account,
            to_object=invoice,
            to_account=invoice.get_accounts_receivable(),
        )
