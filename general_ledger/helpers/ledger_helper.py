from decimal import Decimal
from typing import List

from django.db import transaction
from django.db.models import DecimalField
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from loguru import logger
from rich.console import Console
from rich.text import Text

from general_ledger.builders.transaction import TransactionBuilder
from general_ledger.builders.account_set_summary_builder import AccountSetSummaryBuilder
from general_ledger.builders.account_summary_builder import AccountSummaryBuilder
from general_ledger.django.models.account import Account
from general_ledger.django.models.direction import Direction
from general_ledger.django.models.ledger import Ledger
from general_ledger.django.models.transaction_entry import Entry
from general_ledger.render.consoler import pr_account_balanced
from general_ledger.render.format_table_rich_trial_balance import TrialBalance
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.utility_rich import lists_to_grid_cols
from general_ledger.statements.account_summary import AccountSummary
from general_ledger.statements.ledger_account import LedgerAccount

console = Console()


class LedgerHelper:

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def get_ledger(self):
        return self.ledger

    def get_ledger_name(self):
        return self.ledger.name

    def get_ledger_book(self):
        return self.ledger.book

    @staticmethod
    def account(ledger, account):
        return LedgerAccount(ledger, account)

    @staticmethod
    def accounts(ledger):
        return ledger.coa.account_set.all()

    @staticmethod
    def ledger_accounts(ledger):
        return [
            LedgerAccount(ledger, account) for account in ledger.coa.account_set.all()
        ]

    @staticmethod
    def close_out_by_type_slug(
        ledger, slug, to_account: Account, date, description=None
    ):
        assert to_account is not None, "To account must be provided"

        if not description:
            description = f"Transfer from type '{slug}' ->  {to_account.name}"

        from_accounts = Account.objects.filter(
            coa=ledger.coa,
            type__slug=slug,
        )
        if not from_accounts.count():
            raise ValueError(f"No accounts found for type '{slug}'")
        entries = []
        for from_account in from_accounts:
            amount = ledger.balance_for_account(from_account, date)
            entries.append(
                (from_account, amount, from_account.type.direction.opposite())
            )
            entries.append((to_account, amount, from_account.type.direction))
            logger.trace(
                f"from_account: <{from_account}> type: '{from_account.type.direction.opposite()}' amount: '{amount}'"
            )
            logger.trace(
                f"to_account:   <{to_account}> type: '{from_account.type.direction}' amount: '{amount}'"
            )

        LedgerHelper.post_transaction(ledger, description, date, entries)

    @staticmethod
    def transfer(
        ledger,
        from_account: Account,
        to_account: Account,
        date,
        amount: Decimal,
        description=None,
    ):
        assert from_account.coa == to_account.coa, "Accounts must be in the same coa"
        assert amount > 0, "Amount must be positive"
        assert from_account != to_account, "From and to accounts must be different"
        if not description:
            description = (
                f"Transfer from type '{to_account.name}' ->  {to_account.name}"
            )

        entries = []
        entries.append((from_account, amount, from_account.type.direction.opposite()))
        entries.append((to_account, amount, from_account.type.direction))
        LedgerHelper.post_transaction(ledger, description, date, entries)

    @staticmethod
    def post_transaction(ledger, description, date, entries):
        """
        post a simple transaction
        :param ledger:
        :param description:
        :param date:
        :param entries:
        :return:
        """
        tb = TransactionBuilder(
            ledger=ledger,
            description=description,
        )
        tb.set_trans_date(date)
        for account, amount, direction in entries:
            tb.add_entry(account, amount, direction)
        return tb.build().post()

    @classmethod
    @transaction.atomic
    def get_account_balance(cls, account: Account):
        cr = Entry.objects.filter(
            account=account,
            tx_type=Direction.CREDIT,
        ).aggregate(
            total=Coalesce(
                Sum(
                    "amount",
                ),
                0.0,
                output_field=DecimalField(),
            ),
        )["total"]
        db = Entry.objects.filter(
            account=account,
            tx_type=Direction.DEBIT,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            ),
        )["total"]
        logger.debug(f"cr: {cr} db: {db}")
        return db - cr

    def get_accounts_summary_as_list(self):
        output = []
        for account in Account.objects.annotate(num_txs=Count("entry")).filter(
            num_txs__gt=0, coa__ledger=self.ledger
        ):
            balanced = (
                AccountSummaryBuilder(strict_dates=False)
                .with_account(account)
                .with_ledger(self.ledger)
                .build()
            )
            balanced.balance_off()
            output.append(
                pr_account_balanced(balanced.entries_grouped, title=account.name)
            )
        return output

    def get_account_summary(self):
        output = ""
        for account in Account.objects.annotate(num_txs=Count("entry")).filter(
            num_txs__gt=0,
            coa__ledger=self.ledger,
        ):
            balanced = (
                AccountSummaryBuilder(strict_dates=False)
                .with_account(account)
                .with_ledger(self.ledger)
                .build()
            )
            balanced.balance_off()
            output += pr_account_balanced(balanced.entries_grouped, title=account.name)
        return output

    @staticmethod
    def balanced_to_account_sets(balanced, *args, **kwargs):
        """this is some dumb stuff to get from accounts to account_sets"""
        summary_set = (
            AccountSetSummaryBuilder()
            # .with_entry_set(entry_set)
            .with_summary_set(balanced)
            .with_start_date(kwargs.pop("start_date", None))
            .with_end_date(kwargs.pop("end_date", None))
            .build()
        )
        return summary_set

    @staticmethod
    def render_account_set_summary(summary_set, **kwargs):
        summary_set.set_renderer(RichConsoleRenderer())
        summary_set.set_table_format(
            TrialBalance(),
            **kwargs,
        )
        return summary_set.render()

    @staticmethod
    def accounts_to_summaries(ledger_accounts, **kwargs) -> List[AccountSummary]:
        summaries = [
            LedgerHelper.account_to_summary(ledger_account, **kwargs)
            for ledger_account in ledger_accounts
        ]
        return summaries

    @staticmethod
    def account_to_summary(ledger_account, **kwargs):
        summary = (
            AccountSummaryBuilder(strict_dates=False)
            # .with_entry_set(entry_set)
            .with_account(ledger_account.account)
            .with_ledger(ledger_account.ledger)
            .with_start_date(kwargs.get("start_date", None))
            .with_end_date(kwargs.get("end_date", None))
            .with_balance_interval(kwargs.get("balance_interval", "month"))
            .with_details(
                title=ledger_account.account.name,
                caption="This is a caption",
                currency=ledger_account.account.currency,
            )
            .with_final_balance(kwargs.get("final_balance", False))
            .build()
        )
        if not summary.entries:
            logger.trace("account {account.name} has no entries, skipping")
        else:
            return summary

    @staticmethod
    def summaries_to_balanced(summaries):
        return [
            LedgerHelper.summary_to_balanced(summary)
            for summary in summaries
            if summary and summary.entries
        ]

    @staticmethod
    def summary_to_balanced(summary):
        return summary.balance_off()

    @staticmethod
    def balanced_to_t_accounts(summaries):
        items = []
        for summary in summaries:
            summary.set_renderer(
                RichConsoleRenderer(
                    decimal_format="8,.0f",
                    date_format="%b %e",
                    # highlight_debitors=True,
                    highlight_creditors=False,
                )
            )
            items.append(summary.render())
        return items

    @staticmethod
    def accounts_to_renderables(ledger_account):
        return LedgerHelper.balanced_to_t_accounts(
            LedgerHelper.summaries_to_balanced(
                LedgerHelper.accounts_to_summaries(ledger_account)
            )
        )

    @staticmethod
    def t_accounts_to_grid_col(accounts, ledger):
        items = []
        for account in accounts:
            summary = (
                AccountSummaryBuilder(strict_dates=False)
                # .with_entry_set(entry_set)
                .with_account(account)
                .with_ledger(ledger)
                .with_balance_interval("month")
                .with_details(
                    title=None,
                    caption="This is a caption",
                    currency=None,
                )
                .with_final_balance()
                # .with_by_group_intervals(
                #     [],
                # )
                # .with_start_date("2023-06-01")
                .build()
            )
            if summary.entries:
                # print(f"processing account {account} ledger {ledger}")
                summary.balance_off()
                summary.set_renderer(
                    RichConsoleRenderer(
                        decimal_format="8,.0f",
                        date_format="%b %e",
                        # highlight_debitors=True,
                        highlight_creditors=False,
                    )
                )
                items.append(summary.render())
        return items

    @staticmethod
    def do_account_balancer_accounts(ledger=None, accounts=None, entry_set=None):
        ab = (
            AccountSummaryBuilder(
                strict_dates=False,
            )
            .with_entry_set(entry_set)
            .build()
        )
        ab.balance_off()
        output = pr_account_balanced(ab.entries_grouped)
        return Text.from_ansi(output)

    @staticmethod
    def do_stuff1(
        ledger_accounts,
        do_print=True,
        *args,
        **kwargs,
    ):
        # print(pr_account_list(ledger, accounts))

        summaries = LedgerHelper.accounts_to_summaries(
            ledger_accounts,
            final_balance=True,
            **kwargs,
        )
        balanced = LedgerHelper.summaries_to_balanced(summaries)
        t_accounts = LedgerHelper.balanced_to_t_accounts(balanced)

        summary_set = LedgerHelper.balanced_to_account_sets(
            balanced,
            **kwargs,
        )

        # inspect(col_left)

        if do_print:
            console.print(
                lists_to_grid_cols(
                    t_accounts,
                    LedgerHelper.render_account_set_summary(summary_set),
                    random_styles=False,
                )
            )

        return summary_set

    @staticmethod
    def quick_summary_set(**kwargs):
        ledger = kwargs.get("ledger")

        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        # return a list of AccountSummary with entries by date period
        summaries = LedgerHelper.accounts_to_summaries(ledger_accounts, **kwargs)
        balanced = LedgerHelper.summaries_to_balanced(summaries)
        return LedgerHelper.balanced_to_account_sets(
            balanced,
            **kwargs,
        )
