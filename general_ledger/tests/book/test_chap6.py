from decimal import Decimal

import pytest
from django.db.models import Count
from rich.console import Console

from general_ledger.builders.account_set_summary_builder import AccountSetSummaryBuilder
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.tests.book.data_chap6 import (
    load_chapter_6_data,
    load_chapter_6_review_6_1_data,
    load_chapter_6_review_6_2_data,
    load_chapter_6_review_6_5_data,
)
from general_ledger.render.consoler import pr_account_list

from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.format_table_rich_trial_balance import TrialBalance
from general_ledger.render.utility_rich import lists_to_grid_cols

console = Console()


class TestChapter6TrialBalance:
    """
    trial balance stuff
    """

    @pytest.mark.django_db
    def test_chap_6_2_show_balanced_accounts(self):
        """
        print the accounts defined earlier in balanced off T-account format
        :return:
        """

        print("")

        ledger = load_chapter_6_data()

        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            start_date="2020-05-01",
            end_date="2020-05-31",
        )
        balanced = LedgerHelper.summaries_to_balanced(summaries)
        t_accounts = LedgerHelper.balanced_to_t_accounts(balanced)

        summary_set = (
            AccountSetSummaryBuilder()
            # .with_entry_set(entry_set)
            .with_summary_set(balanced)
            .with_start_date("2020-05-01")
            .with_end_date("2020-05-31")
            .build()
        )

        summary_set.set_renderer(RichConsoleRenderer())
        summary_set.set_table_format(
            TrialBalance(),
            decimal_format="8,.0f",
            date_format="%b  %e",
        )

        # inspect(accounts)
        col_left = t_accounts
        col_right = summary_set.render()

        # inspect(col_left)

        grid = lists_to_grid_cols(
            col_left,
            col_right,
            random_styles=False,
        )
        console.print(grid)
        # console.print(lists_to_grid_cols(col_left))

    @pytest.mark.django_db
    def test_chap_6_review_6_1(self):
        """
        print the accounts defined earlier in balanced off T-account format
        :return:
        """

        print("")

        ledger = load_chapter_6_review_6_1_data()
        accounts = ledger.coa.account_set.order_by("name")
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        print(pr_account_list(ledger, accounts))

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            start_date="2020-05-01",
            end_date="2020-05-31",
            final_balance=True,
        )
        balanced = LedgerHelper.summaries_to_balanced(summaries)
        t_accounts = LedgerHelper.balanced_to_t_accounts(balanced)

        summary_set = LedgerHelper.balanced_to_account_sets(
            balanced,
            start_date="2020-05-01",
            end_date="2020-05-31",
            decimal_format="8,.0f",
        )

        # inspect(col_left)

        console.print(
            lists_to_grid_cols(
                t_accounts,
                LedgerHelper.render_account_set_summary(summary_set),
                random_styles=False,
            )
        )

        assert summary_set.trial_debit_balance == Decimal("4600")
        assert summary_set.trial_credit_balance == Decimal("4600")

    @pytest.mark.django_db
    def test_chap_6_review_6_2(self):
        """
        print the accounts defined earlier in balanced off T-account format
        :return:
        """

        print("")

        ledger = load_chapter_6_review_6_2_data()
        accounts = ledger.coa.account_set.order_by("name")
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        print(pr_account_list(ledger, accounts))

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            start_date="2023-08-01",
            end_date="2023-08-31",
            final_balance=True,
        )
        balanced = LedgerHelper.summaries_to_balanced(summaries)
        t_accounts = LedgerHelper.balanced_to_t_accounts(balanced)

        summary_set = LedgerHelper.balanced_to_account_sets(
            balanced,
            start_date="2023-08-01",
            end_date="2023-08-31",
            decimal_format="8,.0f",
        )

        # inspect(col_left)

        console.print(
            lists_to_grid_cols(
                t_accounts,
                LedgerHelper.render_account_set_summary(summary_set),
                random_styles=False,
            )
        )

        assert summary_set.trial_debit_balance == Decimal("7007")
        assert summary_set.trial_credit_balance == Decimal("7007")

    @pytest.mark.django_db
    def test_chap_6_review_6_5(self):
        """
        print the accounts defined earlier in balanced off T-account format
        :return:
        """

        print("")

        ledger = load_chapter_6_review_6_5_data()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        accounts = ledger.account_set.annotate(entry_count=Count("entry")).filter(
            entry_count__gt=0
        )
        print(pr_account_list(ledger, accounts))

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            start_date="2023-04-01",
            end_date="2023-04-30",
            final_balance=True,
        )
        # print(summaries)

        balanced = LedgerHelper.summaries_to_balanced(summaries)
        t_accounts = LedgerHelper.balanced_to_t_accounts(balanced)

        # print(balanced)

        summary_set = LedgerHelper.balanced_to_account_sets(
            balanced,
            start_date="2023-04-01",
            end_date="2023-04-30",
            decimal_format="8,.0f",
        )

        # inspect(col_left)

        console.print(
            lists_to_grid_cols(
                t_accounts,
                LedgerHelper.render_account_set_summary(summary_set),
                random_styles=False,
            )
        )

        assert summary_set.trial_debit_balance == Decimal("5080")
        assert summary_set.trial_credit_balance == Decimal("5080")
        # @TODO make account summary only return relevant accounts
        assert len(summary_set.summary_set) == 15
