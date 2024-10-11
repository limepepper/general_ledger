import pytest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from general_ledger.factories import TransactionFactory, LedgerFactory
from general_ledger.helpers.ledger_helper import LedgerHelper

# from rich import print

console = Console()


class TestChap5WoodsPyTests:
    @pytest.mark.django_db
    def test_balancing_off_simple_1(self):
        print("")
        print(f"This statement gets mixed with pytest output")
        ledger = LedgerFactory()

        accounts = ledger.account_set.filter(
            slug__in=[
                "bank-account",
                "sales",
                "accounts-receivable",
            ]
        )

        transactions = TransactionFactory.create_batch(
            50,
            ledger=ledger,
            trans_date__start_date="-1y",
            create_transaction_entry_lines__accounts=accounts,
        )

        items_left = LedgerHelper.t_accounts_to_grid_col(accounts, ledger)

        # entry_set = accounts_receivable.entry_set.filter(
        #     transaction__ledger=ledger,
        # )

        items_right = []
        for foo in accounts:
            entry_set = foo.entry_set.filter(
                transaction__ledger=ledger,
            )
            items_right.append(
                LedgerHelper.do_account_balancer_accounts(
                    entry_set=entry_set,
                )
            )

        grid = Table.grid()
        grid.add_column()
        grid.add_column()
        for i, item in enumerate(accounts):
            grid.add_row(items_left[i], items_right[i])

        panel = Panel(grid, expand=True)
        console.print(panel)
