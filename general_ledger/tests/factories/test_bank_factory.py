from django.test import TestCase
from rich import inspect

from general_ledger.factories import BankAccountFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.models import Bank, Account
from general_ledger.models.bank_statement_line_type import BankStatementLineType


class TestBankAccountFactory(TestCase):
    def test_create_bank_account(self):
        bank = BankAccountFactory()
        # inspect(bank)
        self.assertTrue(isinstance(bank, Bank))
        self.assertTrue(isinstance(bank.account, Account))
        self.assertEqual(bank.account.name, bank.name)
        self.assertIn(bank.type, Bank.TYPE_CHOICES)

        savings = BankAccountFactory(type=Bank.SAVINGS)
        self.assertEqual(savings.type, Bank.SAVINGS)

        savings = BankAccountFactory(type=Bank.CHECKING)
        self.assertEqual(savings.type, Bank.CHECKING)

    def test_create_bank_with_transactions(self):
        """
        test create a random bunch of transactions with
        no matching invoices or payments etc. for making
        memo matches.
        :return:
        """
        bank = BankAccountFactory.create_with_transactions(
            num_transactions=100,
        )

        self.assertTrue(isinstance(bank, Bank))
        self.assertTrue(isinstance(bank.account, Account))

        self.assertEqual(bank.bankstatementline_set.count(), 100)

    def test_generate_xfers(self):

        bank_1 = BankAccountFactory(type=Bank.CHECKING)
        bank_2 = BankAccountFactory(type=Bank.SAVINGS)

        txs = BankTransactionFactory.create_transfers(
            50,
            [bank_1, bank_2],
        )

        self.assertEqual(len(txs), 100)

        # test

    def test_types_for_amount_direction(self):
        """
        Test that the amount is positive for payments and negative for debits
        :return:
        """

        assert BankTransactionFactory(type=BankStatementLineType.CREDIT).amount > 0

        assert (
            BankTransactionFactory(
                type=BankStatementLineType.DEBIT,
            ).amount
            < 0
        )

        assert BankTransactionFactory(type=BankStatementLineType.DIV).amount > 0
        #
        assert BankTransactionFactory(type=BankStatementLineType.INT).amount > 0
