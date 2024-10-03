import pytest

from general_ledger.factories import BankAccountFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory


class TestBankTransactions:

    @pytest.mark.django_db
    def test_bank_transactions_types(self):

        bank = BankAccountFactory()
        txs = BankTransactionFactory.create_batch(
            100,
            bank=bank,
        )

        for tx in txs:
            print(f"{tx.type:<18} {tx.amount:>8}")
