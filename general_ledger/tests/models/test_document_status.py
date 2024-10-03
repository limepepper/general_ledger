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
class DocumentStatusTests(GeneralLedgerBaseTest):

    def test_document_status(self):
        book = Book.objects.first()
        ledger = book.get_default_ledger()

        payment = Payment.objects.create(
            date="2022-01-01",
            amount=100,
            ledger=ledger,
        )

        payment.to_state_recorded()
        payment.save()
        # inspect(payment.state)
        payment.refresh_from_db()
        # inspect(payment.state)

        print(payment.state)
        print(DocumentStatus.RECORDED)
        print(payment.state == DocumentStatus.RECORDED)
        print(payment.state == DocumentStatus.DRAFT)

        # payment.state = DocumentStatus.VOID

        # inspect(payment)
