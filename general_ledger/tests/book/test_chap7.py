from datetime import date
from decimal import Decimal

import pytest
from rich.console import Console

from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.format_statement_rich_tree import StatementTreeFormat
from general_ledger.render.format_table_rich_trial_balance import TrialBalance
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.render.utility_rich import ConsoleReportBuilder, lists_to_grid_cols
from general_ledger.statements.meta import NodeMeta, DetailLevel
from general_ledger.statements.nodes.income_statement import IncomeStatementNode
from general_ledger.statements.nodes.trading_account import TradingAccountNode
from general_ledger.statements.provider_django import DjangoProvider
from general_ledger.tests.book.data_chap7 import (
    load_chapter_7_exhibit_7_1,
    load_chapter_7_exhibit_7_3,
    load_chapter_7_review_7_2,
    load_chapter_7_review_7_5,
)
from general_ledger.utils.data_loader import tx

console = Console()


class TestChapter7IncomeStatement:
    """
    trial balance stuff
    """

    def setup_method(self):
        print("")

    @pytest.mark.django_db
    def test_chap_7_exhibit_7_1(self):
        """
        load the data and sanity check the trial balance
        :return:
        """
        print("")

        ledger = load_chapter_7_exhibit_7_1()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        kwargs = {
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
        }

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            **kwargs,
        )
        balanced = LedgerHelper.summaries_to_balanced(summaries)

        summary_set = LedgerHelper.balanced_to_account_sets(
            balanced,
            **kwargs,
        )
        assert summary_set.trial_debit_balance == Decimal("67600")
        assert summary_set.trial_credit_balance == Decimal("67600")

    @pytest.mark.django_db
    def test_chap_7_trading_account_1(self):
        print("")

        ledger = load_chapter_7_exhibit_7_1()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)
        provider = DjangoProvider(ledger=ledger)

        context = {
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
            "provider": provider,
        }
        # print(pr_account_list(ledger, accounts))

        LedgerHelper.do_stuff1(ledger_accounts, do_print=False, **context)

        trading_account = TradingAccountNode(
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()

        console.print(trading_account)
        # inspect(ledger_accounts)

    @pytest.mark.django_db
    def test_chap_7_exhibit_7_3(self):
        print("")

        ledger = load_chapter_7_exhibit_7_3()
        kwargs = {
            "start_date": "2019-01-01",
            "end_date": "2019-12-31",
            "balance_interval": "year",
            "ledger": ledger,
        }
        summary_set = LedgerHelper.quick_summary_set(**kwargs)
        # @TODO this needs the renderer set or it fails...?!?
        summary_set.set_renderer(RichConsoleRenderer())
        summary_set.set_table_format(
            TrialBalance(),
            **kwargs,
        )
        console.print(summary_set.render())

    @pytest.mark.django_db
    def test_chap_7_review_7_2(self):

        ledger = load_chapter_7_review_7_2()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)
        provider = DjangoProvider(ledger=ledger)
        context = {
            "provider": provider,
            "start_date": "2023-7-1",
            "end_date": "2024-06-30",
            "balance_interval": "year",
            "ledger": ledger,
        }

        statement = (
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
        statement.set_renderer(StatementRenderer())
        statement.set_render_format(
            "statement",
            StatementFormatRichTable(),
            # detail_level=DetailLevel.FULL,
        ).render()
        statement.set_renderer(StatementRenderer())
        statement.set_render_format(
            "statement",
            StatementTreeFormat(),
            detail_level=DetailLevel.FULL,
        ).render()

    @pytest.mark.django_db
    def test_chap_7_review_7_5(self):
        """
        load the data and produce the trial balance without the inventory
        as this is applied directly to the trading account
        """

        ledger = load_chapter_7_review_7_5()
        coa = ledger.book.get_default_coa()
        provider = DjangoProvider(ledger=ledger)

        context = {
            "provider": provider,
            "ledger": ledger,
            "balance_interval": "month",
            "start_date": "2023-9-1",
            "end_date": "2023-9-30",
            "final_balance": True,
        }

        summary_set = LedgerHelper.quick_summary_set(**context)

        report = ConsoleReportBuilder().add_column_item("left", summary_set.render())
        trial_balance = summary_set.set_table_format(TrialBalance()).render()

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
                (inventory, "570", "2023-09-30", opening_balances),
            ]
        ]
        statement = (
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
                StatementFormatRichTable(),
            )
        )
        report.add_column_item(
            "right",
            lists_to_grid_cols(
                [trial_balance, statement],
            ),
        )

        console.print(report.build())

        statement = IncomeStatementNode(
            label="Income Statement",
            meta=NodeMeta(
                show_subtotal=True,
            ),
            **context,
        ).ensure_expanded()

        statement.set_renderer(StatementRenderer())
        statement.set_render_format(
            "statement",
            StatementFormatRichTable(),
            # detail_level=DetailLevel.FULL,
        ).render()
