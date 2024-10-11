import pytest
from rich import print as rprint
from rich.console import Console
from rich.pretty import Pretty

from general_ledger.django.models import Account
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.format_statement_rich_tree import StatementTreeFormat
from general_ledger.render.format_table_rich_trial_balance import TrialBalance
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.render.utility_rich import ConsoleReportBuilder, lists_to_grid_cols
from general_ledger.statements.meta import (
    NodeMeta,
    DetailLevel,
    AddOperation,
    Operation,
)
from general_ledger.statements.nodes.balance_sheet import BalanceSheetNode
from general_ledger.statements.nodes.capital import CapitalNode
from general_ledger.statements.nodes.income_statement import IncomeStatementNode
from general_ledger.statements.provider_django import DjangoProvider
from general_ledger.tests.book.data_chap7 import load_chapter_7_exhibit_7_1
from general_ledger.tests.book.data_chap8 import load_chapter_8_exhibit_8_1
from general_ledger.utils.data_loader import tx

console = Console()


class TestChapter8BalanceSheets:
    """Balance Sheet stuff"""

    @pytest.mark.django_db
    def test_chap_8_exhibit_8_1(self):
        """
        load the data and sanity check the trial balance
        :return:
        """

        ledger = load_chapter_8_exhibit_8_1()
        provider = DjangoProvider(ledger=ledger)
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        context = {
            "provider": provider,
            "ledger": ledger,
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
        }
        summary_set = LedgerHelper.quick_summary_set(**context)

        # need to set renderer before setting table format
        summary_set.set_renderer(RichConsoleRenderer())

        statement = BalanceSheetNode(
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()

        report = (
            ConsoleReportBuilder()
            .add_column_item("left", summary_set.render())
            .add_column_item(
                "right",
                lists_to_grid_cols(
                    [
                        summary_set.set_table_format(TrialBalance()).render(),
                        statement.render(),
                    ],
                ),
            )
            .build()
        )

        console.print(report)

    @pytest.mark.django_db
    def test_chap_8_exhibit_8_5(self):
        """
        load the data and sanity check the trial balance
        :return:
        """

        # ledger = load_chapter_8_exhibit_8_1()
        ledger = load_chapter_7_exhibit_7_1()
        coa = ledger.book.get_default_coa()
        provider = DjangoProvider(ledger=ledger)

        # fmt: off
        inventory, opening_balances = [
            coa.get_or_create(*args)
            for k, (args) in {
                "inventory": ["Inventory", "inventory", "no-vat"],
                "opening_balances": ["Opening Balances", "equity", "no-vat"],
            }.items()
        ]
        # fmt: on

        txs = [
            tx(ledger, dr, amt, dt, cr)
            for dr, amt, dt, cr in [
                # applied in the calculation of the trading account
                (inventory, "3000", "2019-12-31", opening_balances),
            ]
        ]

        # ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        context = {
            "provider": provider,
            "ledger": ledger,
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
        }
        summary_set = LedgerHelper.quick_summary_set(**context)

        statement = BalanceSheetNode(
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()

        item1 = statement.render()

        statement.set_renderer(StatementRenderer())
        item2 = statement.set_render_format(
            "statement",
            StatementTreeFormat(),
            detail_level=DetailLevel.FULL,
        ).render()

        item_statement_3 = (
            IncomeStatementNode(
                meta=NodeMeta(
                    show_subtotal=True,
                ),
                label="Income Statement",
                **context,
            )
            .ensure_expanded()
            .prune_empty()
        ).render()

        statement4 = CapitalNode(
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()
        statement4.set_renderer(StatementRenderer())

        item5 = statement4.set_render_format(
            "statement",
            StatementTreeFormat(),
            detail_level=DetailLevel.FULL,
        ).render()

        report = (
            ConsoleReportBuilder()
            .add_column_item(
                "left",
                lists_to_grid_cols(
                    [
                        summary_set.render(),
                    ]
                ),
            )
            .add_column_item(
                "right",
                lists_to_grid_cols(
                    [
                        summary_set.set_table_format(TrialBalance()).render(),
                        item1,
                        item_statement_3,
                        item2,
                        statement4,
                        item5,
                    ],
                ),
            )
            .build()
        )

        console.print(report)

        rprint(Account.objects.all())

    @pytest.mark.django_db
    def test_chap_8_exhibit_8_5_b(self):

        ledger = load_chapter_7_exhibit_7_1()
        coa = ledger.book.get_default_coa()
        provider = DjangoProvider(ledger=ledger)

        context = {
            "provider": provider,
            "ledger": ledger,
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
        }
        # fmt: off
        inventory, opening_balances = [
            coa.get_or_create(*args)
            for k, (args) in {
                "inventory": ["Inventory", "inventory", "no-vat"],
                "opening_balances": ["Opening Balances", "equity", "no-vat"],
            }.items()
        ]
        # fmt: on

        txs = [
            tx(ledger, dr, amt, dt, cr)
            for dr, amt, dt, cr in [
                # applied in the calculation of the trading account
                (inventory, "3000", "2019-12-31", opening_balances),
            ]
        ]

        capital_node = CapitalNode(
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()

        income_statement = (
            IncomeStatementNode(
                label="Income Statement",
                operation=AddOperation,
                meta=NodeMeta(
                    show_subtotal=True,
                    operation=Operation.ADD,
                    expand=DetailLevel.VALUE,
                ),
                **context,
            ).ensure_expanded()
            # .prune_empty()
        )

        console.print(Pretty(income_statement))

        capital_node.find("Capital").add_child(income_statement)

        capital_node.set_renderer(StatementRenderer())
        right1 = capital_node.set_render_format(
            "statement",
            StatementFormatRichTable(),
            # detail_level=DetailLevel.FULL,
        ).render()

        capital_node.set_renderer(StatementRenderer())
        left1 = capital_node.set_render_format(
            "statement",
            StatementTreeFormat(),
            detail_level=DetailLevel.FULL,
        ).render()

        report = (
            ConsoleReportBuilder()
            .add_column_item(
                "left",
                lists_to_grid_cols(
                    [
                        left1,
                    ]
                ),
            )
            .add_column_item(
                "right",
                lists_to_grid_cols(
                    [
                        right1,
                    ],
                ),
            )
            .build()
        )

        console.print(report)

        rprint(Account.objects.all())
