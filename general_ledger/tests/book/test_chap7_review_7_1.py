import pytest
from rich.console import Console

from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.format_statement_rich_table_reversed import (
    StatementTableFormatReverse,
)
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.render.utility_rich import ConsoleReportBuilder, lists_to_grid_cols
from general_ledger.statements.meta import NodeMeta
from general_ledger.statements.nodes.income_statement import IncomeStatementNode
from general_ledger.statements.provider_django import DjangoProvider
from general_ledger.tests.book.data_chap7 import (
    load_chapter_7_review_7_1,
)

console = Console()


class TestChapter7IncomeStatement:
    """
    trial balance stuff
    """

    def setup_method(self):
        print("")

    @pytest.mark.django_db
    def test_chap_7_review_7_1(self):
        print("")

        ledger = load_chapter_7_review_7_1()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)
        provider = DjangoProvider(ledger=ledger)
        context = {
            "provider": provider,
            "ledger": ledger,
            "start_date": "2022-11-01",
            "end_date": "2023-10-31",
            "balance_interval": "year",
        }

        report = ConsoleReportBuilder()

        statement1 = (
            IncomeStatementNode(
                meta=NodeMeta(
                    show_subtotal=True,
                ),
                label="Income Statement",
                **context,
            )
            .ensure_expanded()
            .prune_empty()
        )

        statement1.set_renderer(
            StatementRenderer(),
        )
        statement1.set_render_format(
            "statement",
            StatementFormatRichTable(),
            # detail_level=DetailLevel.FULL,
        )
        # statement.set_renderer(StatementRenderer())

        report.add_column_item("left", statement1)

        provider = DjangoProvider(ledger=ledger)
        statement2 = (
            IncomeStatementNode(
                meta=NodeMeta(
                    show_subtotal=True,
                ),
                **context,
            )
            .ensure_expanded()
            .set_renderer(StatementRenderer())
            .set_render_format(
                "statement",
                StatementTableFormatReverse(),
            )
        )

        report.add_column_item(
            "right",
            lists_to_grid_cols(
                [statement2],
            ),
        )

        console.print(report.build())
