from decimal import Decimal

from decimal import Decimal

from rich import box
from rich.table import Table

from general_ledger.django.models import Direction
from general_ledger.render.formats_abc import TableFormat
from general_ledger.utils.utility_date_stuff import (
    last_day_of,
)


class ThreeColumnFormat(TableFormat):
    """
                                         K Tandy
    -------------------------------------------------------------------------------
                                       Debit             Credit           Balance
    2012                                           GBP         GBP         GBP
    Aug   1  Sales                     |      144.00|            |      144.00
    Aug  19  Sales                     |      300.00|            |      444.00
    Aug  22  Bank Account              |            |      144.00|      300.00
    Aug  28  Bank Account              |            |      300.00|        0.00

    """

    def __init__(self):
        super().__init__()
        self.config_key = "three_column"
        self.table = Table(
            box=box.SIMPLE,
            show_header=True,
            show_footer=False,
            show_edge=False,
            show_lines=False,
            # caption="this is the end, my beautiful friend",
            caption="",
            highlight=True,
            pad_edge=False,
            min_width=75,
        )
        self.renderer = None
        # self.grid_debits = Table.grid(expand=True)
        # self.grid_credits = Table.grid(expand=True)

    def render_table(self, renderer, account_summary):
        self.renderer = renderer
        renderer.console.print("[bold]3-Column Format[/bold]")
        self.table.title = account_summary.title
        self.table.add_column("Date", justify="left", style="cyan")
        self.table.add_column("Narrative", justify="left", style="magenta")
        self.table.add_column("Debit", justify="center", style="blue")
        self.table.add_column("Debit", justify="center", style="yellow")
        self.table.add_column("Balance", justify="center", style="yellow")
        self.table.add_column("Type", justify="center", style="yellow")
        interval_keys = account_summary.entries_grouped["meta"]["interval_keys"]
        first_interval = True
        current_year = None
        # inspect(account_summary)

        for idx, interval_key in enumerate(interval_keys):

            interval = account_summary.entries_grouped[interval_key]
            self.process_interval(
                account_summary, interval, first_interval, len(interval_keys) == idx + 1
            )
            first_interval = False

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
