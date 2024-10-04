import pytest

from general_ledger.factories import BankAccountFactory
from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
import os
import sys

from rich import print, inspect
from rich.columns import Columns

class TestBankStatementLineFactory:

    @pytest.mark.django_db
    def test_bank_statement_lines_types(self):

        bank = BankAccountFactory()
        txs = BankTransactionFactory.create_batch(
            100,
            bank=bank,
        )

        for tx in txs:
            print(f"{tx.type:<18} '{tx.date}' '{tx.datetime}' '{tx.tz}' {tx.amount:>8}")

        # columns = Columns(list(txs), equal=True, expand=True)
        # inspect(list(txs))
        # print(columns)

