from decimal import Decimal

from rich.box import Box
from rich.table import Table

from general_ledger.builders.account_summary_builder import AccountSummary
from general_ledger.django.models import Direction
from general_ledger.render.formats_abc import TableFormat
from general_ledger.utils.utility_date_stuff import (
    last_day_of,
)

HEADER_BOTTOM_ONLY: Box = Box(
    " ══ \n"  # header top crossbar (called top)
    "    \n"  # head (called head)
    " ══ \n"  # header lower crossbar (called head_row)
    "  │ \n"
    " ─┼ \n"
    " ─┼ \n"
    "  │ \n"
    "  ╵ \n"
)


class TrialBalance(TableFormat):

    def __init__(self):
        super().__init__()
        self.config_key = "trial_balance"
        self.table = Table(
            expand=True,
            box=HEADER_BOTTOM_ONLY,
            show_header=True,
            show_footer=False,
            show_edge=True,
            show_lines=False,
            # caption="this is the end, my beautiful friend",
            caption="",
            highlight=True,
            pad_edge=False,
            # min_width=75,
            # header_style="bold black on dark_sea_green1",
            # row_styles=["yellow on green", "red on white"],
        )
        self.renderer = None
        # self.grid_debits = Table.grid(expand=True)
        # self.grid_credits = Table.grid(expand=True)

    def render_table(self, renderer, account_set):
        self.renderer = renderer
        self.table.title = f"Trial balance as of {account_set.end_date}"
        self.table.add_column("Account", justify="left", style="cyan")
        self.table.add_column("Debit", justify="right", style="magenta")
        self.table.add_column("Credit", justify="right", style="blue")

        for account_summary in account_set.summary_set:
            suffix = account_summary.entries_grouped["suffix"]
            # @TODO make account summary only return relevant accounts
            if suffix["status"] == AccountSummary.Status.EMPTY:
                print(f"Skipping {account_summary.title}")
                continue
            self.table.add_row(
                account_summary.title,
                renderer.factory.fmt(account_summary.debit_balance),
                renderer.factory.fmt(account_summary.credit_balance),
            )

        trial_debit_balance = renderer.factory.fmt(account_set.trial_debit_balance)
        trial_credit_balance = renderer.factory.fmt(account_set.trial_credit_balance)
        debit_line_len = trial_debit_balance.cell_len
        credit_line_len = trial_credit_balance.cell_len
        self.table.add_row(
            "",
            ("-" * debit_line_len),
            ("-" * credit_line_len),
        )
        self.table.add_row(
            "",
            trial_debit_balance,
            trial_credit_balance,
        )
        self.table.add_row(
            "",
            ("=" * debit_line_len),
            ("=" * credit_line_len),
        )

        first_interval = True
        current_year = None
        # inspect(account_summary)

        renderer.renderable = self.table

    def process_interval(
        self, account_summary, interval, first_interval, final_interval
    ):
        current_year = None
        self.table.add_row(interval["interval_key_dt"].strftime("%Y"))
        for idx, row in enumerate(
            self.process_entries_3_col(account_summary, interval)
        ):
            self.table.add_row(*row.as_cols())

    def process_entries_3_col(self, account_summary, interval):
        """
        convert a summary into TEntry objects for rendering
        :param account_summary:
        :param interval:
        :return:
        """
        rows = []
        entries = interval["entries"]
        group_intervals = interval["group_intervals"]
        last_day = last_day_of(
            interval["interval_key_dt"],
            interval["balance_interval"],
        )
        for entry in entries:
            running_balance = entry.running_balance()
            balance_type = (
                ("Dr" if entry.account.type.direction == Direction.DEBIT else "Cr")
                if running_balance
                else ""
            )
            row = self.renderer.factory.threecolentry(
                date=entry.trans_date,
                narrative=entry.get_counter_entry(),
                debit_amount=entry.amount if entry.is_debit else Decimal("0.00"),
                credit_amount=entry.amount if entry.is_credit else Decimal("0.00"),
                balance=running_balance,
                balance_type=balance_type,
            )
            rows.append(row)

        return rows
