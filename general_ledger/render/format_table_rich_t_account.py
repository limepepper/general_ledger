import itertools
from collections import defaultdict
from datetime import datetime

from loguru import logger
from rich.box import Box

from currency_symbols import CurrencySymbols
from rich.padding import Padding
from rich.style import Style
from rich.table import Table
from rich.text import Text

from general_ledger.render.formats_abc import TableFormat
from general_ledger.render.renderables import TTotalEntry, TEmpty, TRow
from general_ledger.render.utility_rich import t_account_col_grid
from general_ledger.utils.inspect import inspect
from general_ledger.utils.utility_date_stuff import (
    last_day_of,
    get_interval_key,
    first_day_of_next,
)

HEADER_BOTTOM_ONLY: Box = Box(
    " ══ \n"  # header top crossbar (called top)
    "  │ \n"  # head (called head)
    " ══ \n"  # header lower crossbar (called head_row)
    "  │ \n"
    " ─┼ \n"
    " ─┼ \n"
    "  │ \n"
    "  ╵ \n"
)


class TAccountFormat(TableFormat):
    """
    ╭──────────────────────────────────────────────────────────────────────────────╮
    │                                   K Tandy                                    │
    │                                  ╷                                           │
    │              Debits              │                 Credits                   │
    │  ════════════════════════════════╪════════════════════════════════════════   │
    │  2012                        £   │ 2012                                £     │
    │  12.8.1    Sales          144.00 │ 12.8.22   Bank Account           144.00   │
    │  12.8.19   Sales          300.00 │ 12.8.28   Bank Account           300.00   │
    │                          ------- │                                 -------   │
    │                           444.00 │                                  444.00   │
    │                          ======= │                                 =======   │
    │                                  ╵                                           │
    │                    this is the end, my beautiful friend                      │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    """

    def __init__(self):
        super().__init__()
        self.config_key = "t_account"
        self.renderer = None

    def render_table(self, renderer, account_summary):
        if not type(account_summary).__name__ == "AccountSummary":
            raise ValueError(
                f"account_summary must be an instance of AccountSummary not '{type(account_summary).__name__}'"
            )
        logger.trace(f"processing account summary {account_summary.title}")
        self.renderer = renderer
        date_fmt = self.renderer.options.get("date_format", "%-m.%-d")

        table = Table(
            expand=True,
            box=HEADER_BOTTOM_ONLY,
            show_header=False,
            show_footer=False,
            show_edge=True,
            show_lines=False,
            # caption="this is the end, my beautiful friend",
            highlight=True,
            pad_edge=False,
            min_width=75,
            # width=80,
            title_style="bold green",
            # collapse_padding=True,
            # padding=(0,),
        )
        table.title = account_summary.title
        table.add_column(
            "",
            justify="center",
            # style=random_style("col"),
            style="magenta",
            ratio=3,
        )
        table.add_column(
            "",
            justify="center",
            # style=random_style("col"),
            style="magenta",
            ratio=3,
        )

        grid_debits, grid_credits = t_account_col_grid()

        if hasattr(account_summary, "entries_grouped"):
            self._process_intervals(
                table, grid_debits, grid_credits, renderer, account_summary
            )
        else:
            inspect(account_summary, methods=True, dunder=True, all=True)
            logger.warning(
                "no entries_grouped in account_summary for '{}'", account_summary
            )
            print(f"account_summary: {account_summary}")
            print(f"account_summary: {account_summary!r}")
        renderer.renderable = table

    def _process_intervals(
        self, table, grid_debits, grid_credits, renderer, account_summary
    ):
        interval_keys = account_summary.entries_grouped["meta"]["interval_keys"]
        first_interval = True
        current_year = None
        # inspect(account_summary)

        for idx, interval_key in enumerate(interval_keys):

            interval = account_summary.entries_grouped[interval_key]
            if current_year is None or interval["interval_key_dt"].year != current_year:
                current_year = interval["interval_key_dt"].year
                self.print_year_header(
                    table, grid_debits, grid_credits, account_summary, current_year
                )
            self.process_interval(
                table,
                grid_debits,
                grid_credits,
                account_summary,
                interval,
                first_interval,
                len(interval_keys) == idx + 1,
            )
            first_interval = False
        # add all the accumulated stuff to the table
        table.add_row(grid_debits, grid_credits)

    def process_interval(
        self,
        table,
        grid_debits,
        grid_credits,
        account_summary,
        interval,
        first_interval,
        final_interval,
    ):
        current_year = None
        # inspect(interval)

        for idx, row in enumerate(self.process_entries(interval)):
            if (
                current_year is None
                or (
                    (row.debit_entry.date.year != current_year)
                    and not isinstance(row.debit_entry, TTotalEntry)
                )
                or (
                    (row.credit_entry.date.year != current_year)
                    and not isinstance(row.credit_entry, TTotalEntry)
                )
            ):
                current_year = row.debit_entry.date.year
                (
                    self.print_year_header(
                        table,
                        grid_debits,
                        grid_credits,
                        account_summary,
                        current_year,
                    )
                    if idx
                    else None
                )
            debit_style = Style(bgcolor="default")
            credit_style = Style(bgcolor="default")

            if interval[
                "status"
            ] == account_summary.Status.DEBIT_BALANCE and self.renderer.options.get(
                "highlight_debitors"
            ):
                debit_style += Style(bgcolor="light_steel_blue1")
            if interval[
                "status"
            ] == account_summary.Status.CREDIT_BALANCE and self.renderer.options.get(
                "highlight_creditors"
            ):
                credit_style += Style(bgcolor="thistle1")
            grid_debits.add_row(*row.debit_entry.as_cols(), style=debit_style)
            grid_credits.add_row(*row.credit_entry.as_cols(), style=credit_style)

        # @TODO this very dumb. no do plz
        if final_interval and account_summary.final_balance:
            # append_final_balance
            row = self.append_final_balance(account_summary, interval)
            if row:
                grid_debits.add_row(*row.debit_entry.as_cols())
                grid_credits.add_row(*row.credit_entry.as_cols())

    def print_year_header(
        self,
        table,
        grid_debits,
        grid_credits,
        account_summary,
        year,
    ):
        grid_debits.add_row(
            f"{year}",
            "  ",
            Padding(
                Text(CurrencySymbols.get_symbol(account_summary.currency)),
                (0, 2, 0, 0),
            ),
            style="bold",
        )
        grid_credits.add_row(
            f"{year}",
            "  ",
            Padding(
                Text(CurrencySymbols.get_symbol(account_summary.currency)),
                (0, 2, 0, 0),
            ),
            style="bold",
        )

    def process_entries(
        self,
        interval,
    ):
        debits_list = []
        credits_list = []
        entries = interval["entries"]
        group_intervals = interval["group_intervals"]

        # find the last day of the interval
        last_day = last_day_of(
            interval["interval_key_dt"],
            interval["balance_interval"],
        )

        grouped_debits = self.append_entries(
            interval,
            entries.debits(),
            "debit_bd",
            "debit_cd",
            group_intervals,
            last_day,
        )
        grouped_credits = self.append_entries(
            interval,
            entries.credits(),
            "credit_bd",
            "credit_cd",
            group_intervals,
            last_day,
        )

        for key in sorted(set(grouped_debits.keys()).union(grouped_credits.keys())):
            debits = grouped_debits[key]
            creditz = grouped_credits[key]
            max_len = max(len(debits), len(creditz))
            padded_debits = debits + [
                TEmpty(date=debits[-1].date if debits else creditz[-1].date)
            ] * (max_len - len(debits))
            padded_credits = creditz + [
                TEmpty(date=creditz[-1].date if creditz else debits[-1].date)
            ] * (max_len - len(creditz))
            debits_list.extend(padded_debits)
            credits_list.extend(padded_credits)

        zipped = list(
            itertools.zip_longest(
                debits_list,
                credits_list,
            )
        )
        rows = []
        for debit, credit in zipped:
            # inspect(credit)
            rows.append(TRow(debit, credit))

        rows.append(
            TRow(
                self.renderer.factory.ttotalentry(
                    last_day, interval["total"], one_line=len(rows) == 1
                ),
                self.renderer.factory.ttotalentry(
                    last_day, interval["total"], one_line=len(rows) == 1
                ),
            )
        )
        return rows

    def append_entries(
        self, interval, entries, bd_key, cd_key, group_intervals, last_day
    ):
        """
        append the entries to the interval
        :param interval:
        :param entries:
        :param bd_key:
        :param cd_key:
        :param group_intervals:
        :param last_day: used to place the cd entry at the end
        :return:
        """
        grouped_entries = defaultdict(list)
        if interval[bd_key]:
            key = get_interval_key(
                interval["interval_key_dt"],
                group_intervals,
            )
            grouped_entries[key].append(
                self.renderer.factory.tbdentry(
                    date=interval["interval_key_dt"],
                    amount=interval[bd_key],
                )
            )

        for entry in entries:
            key = get_interval_key(
                entry.trans_date,
                group_intervals,
            )
            grouped_entries[key].append(
                self.renderer.factory.tentry(
                    date=entry.trans_date,
                    narrative=entry.narrative,
                    amount=entry.amount,
                )
            )
        if interval[cd_key]:
            key = get_interval_key(
                last_day,
                group_intervals,
            )
            grouped_entries[key].append(
                self.renderer.factory.tcdentry(
                    date=last_day,
                    amount=interval[cd_key],
                )
            )
        return grouped_entries

    def append_final_balance(self, account_summary, final_interval):
        # this is pretty dumb. @TODO move this stuff into the account_summary
        if account_summary.balance_interval:
            # if we have an interval, we can calculate the first day
            # of the suffix period
            first_day = first_day_of_next(
                final_interval["interval_key_dt"],
                final_interval["balance_interval"],
            )
        else:
            # else the first day of the suffix is today
            first_day = datetime.today().date()

        interval = account_summary.entries_grouped["suffix"]
        if interval["debit_bd"]:
            return TRow(
                self.renderer.factory.tbdentry(
                    date=first_day,
                    amount=interval["debit_bd"],
                ),
                TEmpty(date=datetime.today().date()),
            )
        elif interval["credit_bd"]:
            return TRow(
                TEmpty(date=datetime.today().date()),
                self.renderer.factory.tbdentry(
                    date=first_day,
                    amount=interval["credit_bd"],
                ),
            )
