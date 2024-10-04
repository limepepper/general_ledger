# import logging

from datetime import datetime, timedelta

import pytest
from faker import Faker

from general_ledger.factories import BankAccountFactory
from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.helpers.bank_balance_helper import BankBalanceHelper

fake = Faker()


class TestBankBalanceHelper:
    @pytest.mark.django_db
    def test_get_bank_balance(self):
        bank = BankAccountFactory()
        txs = BankTransactionFactory.create_batch(
            100,
            bank=bank,
            date__start_date=(datetime.now() - timedelta(days=14)).date(),
            date__end_date=(datetime.now() - timedelta(days=7)).date(),
        )

        for tx in txs:
            print(f"{tx.type:<18} {tx.date} {tx.amount:>8}")

        bbh = BankBalanceHelper(bank)
        balance = bbh.get_balance()

    # @pytest.mark.django_db
    # def test_get_bank_balance_with_date(self):
    #     pass
    #
    # @pytest.mark.django_db
    # def test_get_bank_balance_with_date_range(self):
    #     pass
    #
    # @pytest.mark.django_db
    # def test_get_bank_balance_with_date_range_and_bank_account(self):
    #     pass
