import logging
from decimal import Decimal

from django.template.loader import get_template
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from general_ledger.builders.account_summary_builder import AccountSummaryBuilder
from general_ledger.render.utility_rich import ConsoleReportBuilder
from general_ledger.tests import GeneralLedgerBaseTest
from general_ledger.tests.book.data_chap5 import (
    load_chapter_5_data,
    load_5_review_5_1_data,
    load_5_review_5_2_data,
    load_5_review_5_5_data,
)
from general_ledger.render.consoler import pr_account_balanced
from general_ledger.render.renderables import render_2_cols
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.format_table_rich_three_col import ThreeColumnFormat
from general_ledger.utils.inspect import inspect

# from rich import print

console = Console()


# Create your tests here.
class TestChap5Woods(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_chap_5_1_k_tandy(self):

        print("")

        ledger = load_chapter_5_data()

        k_tandy = ledger.coa.getac("K Tandy")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(k_tandy)
            .with_final_balance()
            .build()
        )

        suffix = account_summary.entries_grouped["suffix"]
        assert suffix["debit_bd"] is None
        assert suffix["credit_bd"] is None
        assert suffix["debit_cd"] is None
        assert suffix["credit_cd"] is None

        assert account_summary.debit_balance == Decimal("0")
        assert account_summary.credit_balance == Decimal("0")
        assert account_summary.debit_total == Decimal("444")
        assert account_summary.credit_total == Decimal("444")

        # inspect(account_summary)
        col1 = account_summary.render()
        col2 = pr_account_balanced(
            account_summary.entries_grouped, title="Account Name"
        )
        console.print(render_2_cols(col1, Text.from_ansi(col2)))
        #        console.print(Text.from_ansi(col2))

        panel = Panel(col1, expand=True)
        console.print(panel)

    def test_chap_5_1_c_lee(self):

        ledger = load_chapter_5_data()

        c_lee = ledger.coa.getac("C Lee")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(c_lee)
            .build()
        )
        account_summary.balance_off()

        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)
        console.print(render_2_cols(col1, Text.from_ansi(col2)))

        suffix = account_summary.entries_grouped["suffix"]
        assert suffix["debit_bd"] is None
        assert suffix["credit_bd"] is None
        assert suffix["debit_cd"] is None
        assert suffix["credit_cd"] is None

        assert account_summary.debit_balance == Decimal("0")
        assert account_summary.credit_balance == Decimal("0")
        assert account_summary.debit_total == Decimal("480")
        assert account_summary.credit_total == Decimal("480")

    def test_chap_5_1_k_wood(self):

        ledger = load_chapter_5_data()

        k_wood = ledger.coa.getac("K Wood")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(k_wood)
            # .with_start_date("2012-08-15")
            .with_final_balance()
            .build()
        )
        account_summary.balance_off()
        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)

        console.print(render_2_cols(col1, Text.from_ansi(col2)))

        suffix = account_summary.entries_grouped["suffix"]
        assert suffix["debit_bd"] is None
        assert suffix["credit_bd"] is None
        assert suffix["debit_cd"] is None
        assert suffix["credit_cd"] is None

        assert account_summary.debit_balance == Decimal("0")
        assert account_summary.credit_balance == Decimal("0")
        assert account_summary.debit_total == Decimal("214")
        assert account_summary.credit_total == Decimal("214")

    def test_chap_5_1_d_knight(self):

        ledger = load_chapter_5_data()

        d_knight = ledger.coa.getac("D Knight")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(d_knight)
            # .with_start_date("2012-01-15")
            .with_balance_interval("month")
            .with_final_balance()
            .build()
        )
        account_summary.balance_off()
        # inspect(account_summary)
        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)
        console.print(render_2_cols(col1, Text.from_ansi(col2)))

        suffix = account_summary.entries_grouped["suffix"]
        assert suffix["debit_bd"] == Decimal("324.00")
        assert suffix["credit_bd"] is None

        assert account_summary.debit_balance == Decimal("324")
        assert account_summary.credit_balance == Decimal("0")
        assert account_summary.debit_total == Decimal("482")
        assert account_summary.credit_total == Decimal("158")

    def test_chap_5_1_b_walters(self):

        ledger = load_chapter_5_data()

        b_walters = ledger.coa.getac("B Walters")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(b_walters)
            # .with_start_date("2012-08-15")
            # .with_by_group_intervals([])
            .with_balance_interval("month")
            .with_end_date("2012-09-3")
            .with_final_balance()
            .build()
        )
        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)
        console.print(render_2_cols(col1, Text.from_ansi(col2)))

        suffix = account_summary.entries_grouped["suffix"]
        assert suffix["debit_bd"] == Decimal("51.00")
        assert suffix["credit_bd"] is None

    def test_chap_5_2(self):
        """accounts for creditors"""

        print("")
        ledger = load_chapter_5_data()

        e_williams = ledger.coa.getac("E Williams")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(e_williams)
            .with_balance_interval("month")
            .with_final_balance()
            .build()
        )
        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)
        console.print(render_2_cols(col1, Text.from_ansi(col2)))

        e_williams = ledger.coa.getac("K Patterson")

        account_summary = (
            AccountSummaryBuilder(strict_dates=False)
            .with_ledger(ledger=ledger)
            .with_account(e_williams)
            .with_balance_interval("month")
            .with_final_balance()
            .build()
        )
        col1 = account_summary.render()
        col2 = pr_account_balanced(account_summary.entries_grouped)
        console.print(render_2_cols(col1, Text.from_ansi(col2)))

    def test_chap_5_3(self):
        """
        Three columns accounts
        :return:
        """
        print("")
        ledger = load_chapter_5_data()

        accounts = ledger.coa.account_set.filter(
            type__slug__in=[
                "accounts-receivable",
                "accounts-payable",
            ]
        )

        col1_list = []
        grid = Table.grid()
        grid.add_column()

        for account in accounts:
            account_summary = (
                AccountSummaryBuilder(strict_dates=False)
                .with_ledger(ledger=ledger)
                .with_account(account)
                # .with_balance_interval("week")
                .build()
            )
            if account_summary.entries:
                print(f"{account=}")
                # inspect(account_summary)
                account_summary.set_renderer(RichConsoleRenderer())
                account_summary.set_table_format(ThreeColumnFormat())
                out = account_summary.render()
                col1_list.append(out)
                grid.add_row(out)

        template = get_template("gl/console/three_col_accounts.j2")

        context = {
            "ledger": ledger,
            "accounts": accounts,
        }

        self.logger.info(template.render(context=context))
        col2 = template.render(context=context)
        console.print(render_2_cols(grid, Text.from_ansi(col2)))

    def test_chap_5_review_5_1(self):
        """
        Three columns accounts
        :return:
        """
        print("")
        ledger = load_5_review_5_1_data()

        accounts = ledger.coa.account_set.filter(
            type__slug__in=["accounts-receivable", "accounts-payable"]
        )

        grid_left = Table.grid()
        grid_left.add_column()
        grid_right = Table.grid()
        grid_right.add_column()

        for account in accounts:
            summary = (
                AccountSummaryBuilder(strict_dates=False)
                .with_ledger(ledger=ledger)
                .with_account(account)
                .with_final_balance()
                # .with_balance_interval("week")
                .build()
            )
            if summary.entries:
                print(f"{account=}")
                summary.balance_off()
                # inspect(account_summary)
                # account_summary.set_table_format(ThreeColumnFormat())
                grid_left.add_row(summary.render())
                summary.set_table_format(ThreeColumnFormat())
                grid_right.add_row(summary.render())

        console.print(render_2_cols(grid_left, grid_right))

    def test_chap_5_review_5_2(self):
        """
        Three columns accounts
        :return:
        """
        print("")
        ledger = load_5_review_5_2_data()

        accounts = ledger.coa.account_set.filter(
            type__slug__in=["accounts-receivable", "accounts-payable"]
        )

        grid_left = Table.grid()
        grid_left.add_column()
        grid_right = Table.grid()
        grid_right.add_column()

        for account in accounts:
            summary = (
                AccountSummaryBuilder(strict_dates=False)
                .with_ledger(ledger=ledger)
                .with_account(account)
                .with_final_balance()
                .with_balance_interval("month")
                .build()
            )
            if summary.entries:
                print(f"{account=}")
                summary.set_renderer(RichConsoleRenderer())
                grid_left.add_row(summary.render())
                summary.set_table_format(
                    ThreeColumnFormat(),
                    decimal_format="8,.0f",
                    date_format="%b  %e",
                )
                grid_right.add_row(summary.render())

        console.print(render_2_cols(grid_left, grid_right))

    def test_chap_5_review_5_5(self):
        print("")
        ledger = load_5_review_5_5_data()

        accounts = ledger.coa.account_set.filter(
            type__slug__in=[
                "accounts-receivable",
                "accounts-payable",
            ]
        )

        report = ConsoleReportBuilder(panel=True)

        for account in accounts:
            summary = (
                AccountSummaryBuilder(strict_dates=False)
                .with_ledger(ledger=ledger)
                .with_account(account)
                .with_final_balance()
                .with_balance_interval("month")
                .build()
            )
            if summary.entries:
                report.add_column_item(
                    "left",
                    summary.set_renderer(
                        RichConsoleRenderer(
                            decimal_format="8,.0f",
                            date_format="%b %e",
                        )
                    ).render(),
                )
                report.add_column_item(
                    "right",
                    summary.set_renderer(
                        RichConsoleRenderer(
                            decimal_format="8,.0f",
                            date_format="%b %e",
                        )
                    )
                    .set_table_format(
                        ThreeColumnFormat(),
                        decimal_format="8,.0f",
                        date_format="%b  %e",
                    )
                    .render(),
                )

        console.print(report.build())
