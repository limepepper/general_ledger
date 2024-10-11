# from rich import print
from datetime import date

import pytest
from rich.console import Console

from general_ledger.factories import TransactionFactory
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.tests.book.test_chap7 import load_chapter_7_exhibit_7_1

# from rich import print

console = Console()


class TestIncomeStatementBuilder:

    @pytest.mark.django_db
    def test_simple_income_statement_builder_1(self):

        ledger = load_chapter_7_exhibit_7_1()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        accounts = ledger.account_set.filter(
            slug__in=[
                "bank-account",
                "sales",
                "accounts-receivable",
            ]
        )

        transactions = TransactionFactory.create_batch(
            100,
            ledger=ledger,
            trans_date__start_date=date(2018, 11, 15),
            trans_date__end_date=date(2021, 1, 15),
            create_transaction_entry_lines__accounts=accounts,
        )

        kwargs = {
            "start_date": "2018-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
        }

        summary_set = LedgerHelper.do_stuff1(
            ledger_accounts,
            do_print=False,
            **kwargs,
        )

        # console.print(summary_set)

        console.print(summary_set.summary_set)

        # provider = DjangoProvider(ledger=ledger)
        #
        # trading_account = TradingAccountNode(
        #     provider=provider,
        #     meta=NodeMeta(
        #         show_subtotal=True,
        #     ),
        #     **kwargs,
        # )
        #
        # income_statement = IncomeStatement(
        #     ledger=ledger,
        #     trading_account=summary_set.summary_set["sales"],
        #     **kwargs,
        # )

        # inspect(summary_set, dunder=True)
