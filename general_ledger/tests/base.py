from random import randint, choice
from uuid import uuid4

from django.test import TestCase

from general_ledger.models import Book, Ledger


import logging


class GeneralLedgerBaseTest(TestCase):

    logger = logging.getLogger(__name__)

    fixtures = [
        "general_ledger/fixtures/users.yaml",
        "general_ledger/fixtures/account_types.yaml",
        "general_ledger/fixtures/tax_types.yaml",
        "general_ledger/fixtures/coa.yaml",
        "general_ledger/fixtures/tax_rates.yaml",
        "general_ledger/fixtures/books.yaml",
        "general_ledger/fixtures/ledgers.yaml",
        "general_ledger/fixtures/accounts.yaml",
        "general_ledger/fixtures/banks.yaml",
        "general_ledger/fixtures/bank_account_accounts.yaml",
    ]

    # def __init__(self):
    #     print("this is running once per test")

    def setUp(self):
        self.logger.debug("this is running once per test")

    @classmethod
    def setUpTestData(cls):
        cls.logger.debug("Setting up test data")
        # cls.book = Book.objects.create(
        #     name=f"book-{uuid4()}",
        # )
        # cls.ledger = Ledger.objects.create(
        #     name=f"ledger-{uuid4()}",
        #     book=cls.book,
        # )

    def create_empty_ledger(self) -> Ledger:
        return self.book.create_ledger()
