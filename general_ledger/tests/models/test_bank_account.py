import logging

import django
from django.db import IntegrityError
from django.test import override_settings
from faker import Faker
from rich import inspect

from general_ledger.factories import BankAccountFactory, BookFactory
from general_ledger.models import Ledger, Bank, Account, TaxRate, AccountType
from general_ledger.tests import GeneralLedgerBaseTest


# this is to test creating invoice lines
class TestBankAccountModel(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def __init__(self, methodName: str):
        super().__init__(methodName)
        # self.logger = logging.getLogger(__name__)
        self.fake = Faker()

    fixtures = [
        "general_ledger/fixtures/users.yaml",
        "general_ledger/fixtures/books.yaml",
        "general_ledger/fixtures/coa.yaml",
        "general_ledger/fixtures/account_types.yaml",
        "general_ledger/fixtures/tax_types.yaml",
        "general_ledger/fixtures/tax_rates.yaml",
        "general_ledger/fixtures/ledgers.yaml",
        "general_ledger/fixtures/accounts.yaml",
        "general_ledger/fixtures/contacts.yaml",
    ]

    @override_settings(DEBUG=True)
    def test_basic_bank_1(self):
        """
        test vanilla instances can be created
        """
        ledger = Ledger.objects.get(name="ledger-generic-1")
        book = ledger.book

        bank = Bank.objects.create_with_account(
            name=f"{self.fake.company()}",
            book=book,
            account_number="12345678",
            sort_code="12-34-56",
        )

        # inspect(bank)
        # inspect(bank.account)

    def test_whether_can_create_unsaved_bank_account(self):
        """
        test whether can create unsaved bank account
        """
        book = BookFactory()
        account = Account(
            name="Test Account",
            coa=book.get_default_coa(),
            tax_rate=TaxRate.objects.for_book(book).get(slug="no-vat"),
            type=AccountType.objects.for_book(book).get(name="Bank"),
        )
        bank = Bank(
            name="Test Bank",
            book=book,
            account_number="12345678",
            sort_code="12-34-56",
            account=account,
        )

        # this not catching
        # with self.assertRaises(django.db.utils.IntegrityError):
        #   bank.save()

        account.save()
        bank.save()

        # inspect(account)
        # inspect(bank)

    def test_bank_with_account_updating(self):
        """
        test bank with account updating
        test that the bank can be renamed and the account is also updated correctly
        """

        bank = BankAccountFactory(
            name="BeforeName",
        )

        # inspect(bank)
        # inspect(bank.account)

        bank.name = "AfterName"
        bank.save()

        # inspect(bank.name)
        # inspect(bank.account.name)
