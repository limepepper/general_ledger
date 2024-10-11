import pytest
from rich import inspect

from general_ledger.factories import TransactionFactory, LedgerFactory
from general_ledger.django.models import Transaction
from general_ledger.render.consoler import pr_tx_list


class TestTransactionFactory:
    @pytest.mark.django_db
    def test_create_tx_simple_1(self):
        ledger = LedgerFactory()

        transactions = TransactionFactory.create_batch(
            10,
            ledger=ledger,
        )
        # inspect(bank)
        assert isinstance(transactions[0], Transaction)

        inspect(transactions)

    @pytest.mark.django_db
    def test_create_tx_simple_2(self):
        ledger = LedgerFactory()

        # inspect(ledger.coa.account_set.all())

        transactions = TransactionFactory.create_batch(
            10,
            ledger=ledger,
            create_transaction_entry_lines__accounts=ledger.coa.account_set.filter(
                slug__in=[
                    "bank-account",
                    "sales",
                    "accounts-receivable",
                ]
            ),
        )
        # inspect(bank)
        assert isinstance(transactions[0], Transaction)

        print(pr_tx_list(transactions))

        assert transactions[0].entry_set.count() > 0

        # inspect(transactions)
