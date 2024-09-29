import logging

from django.test import override_settings
from faker import Faker
from rich import inspect

from general_ledger.models import Ledger, Bank
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
    def test_stuff1(self):
        """
        test vanilla instances can be created
        """
        ledger = Ledger.objects.get(name="ledger-generic-1")
        book = ledger.book

        suffixes = [
            "Bank",
            "National Bank",
            "Savings and Loans",
            "Mutual",
            "Credit Union",
        ]

        bank, account = Bank.objects.create_with_account(
            name=f"{self.fake.company()}",
            book=book,
            account_number="12345678",
            sort_code="12-34-56",
        )

        inspect(bank)
        inspect(account)
