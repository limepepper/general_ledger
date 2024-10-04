import pytest

from general_ledger.factories import BankAccountFactory, BookFactory
from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.management.utils import (
    get_book,
    get_or_create_customers,
    get_or_create_banks,
)
from general_ledger.models import Bank, Book


class TestGenerateTransfers:

    @pytest.mark.django_db
    def test_generate_bank_xfers(self):
        book = BookFactory()
        bank1 = BankAccountFactory(
            type=Bank.CHECKING,
            book=book,
        )
        bank2 = BankAccountFactory(
            book=book,
            type=Bank.SAVINGS,
            num_banks=1,
        )
        assert isinstance(book, Book)
        assert isinstance(bank1, Bank)
        assert isinstance(bank2, Bank)

        # xfers = BankTransactionFactory.create_with_transactions(
        #     book=book,
        #     type=Bank.CHECKING,
        #     num_banks=1,
        # )

        # create sample transfer transactions between these bank accounts
        for num in range(1, 10):
            xfers = BankTransactionFactory(
                bank=bank1,
                type=Bank.CHECKING,
            )

        # assert xfers
        # assert len(xfers) == num
