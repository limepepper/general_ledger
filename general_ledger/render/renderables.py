from rich.console import Console
from rich.console import ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.table import Table

from general_ledger.render.utility_rich import fmt


def render_2_cols(col1, col2):
    grid = Table.grid()
    grid.add_column()
    grid.add_column()
    grid.add_row(col1, col2)
    panel = Panel(
        grid,
        expand=True,
        padding=0,
    )
    return panel


class RendererContext:
    def __init__(self, options):
        self.options = options


class RendererFactory:
    def __init__(self, context):
        self.context = context

    def fmt(self, *args, **kwargs):
        return fmt(*args, **kwargs, context=self.context)

    def tentry(self, *args, **kwargs):
        return TEntry(*args, **kwargs, context=self.context)

    def trow(self, *args, **kwargs):
        return TRow(*args, **kwargs, context=self.context)

    def tempty(self, *args, **kwargs):
        return TEmpty(*args, **kwargs, context=self.context)

    def tcdentry(self, *args, **kwargs):
        return TCDEntry(*args, **kwargs, context=self.context)

    def tbdentry(self, *args, **kwargs):
        return TBDEntry(*args, **kwargs, context=self.context)

    def ttotalentry(self, *args, **kwargs):
        return TTotalEntry(*args, **kwargs, context=self.context)

    def threecolentry(self, *args, **kwargs):
        return ThreeColEntry(*args, **kwargs, context=self.context)


class ThreeColEntry:
    """
    represents a single entry in a Three col account
    """

    def __init__(
        self,
        date,
        narrative,
        debit_amount,
        credit_amount,
        balance,
        balance_type,
        folio=None,
        context=None,
    ):
        self.date = date
        self.narrative = narrative
        self.debit_amount = debit_amount
        self.credit_amount = credit_amount
        self.balance = balance
        self.balance_type = balance_type
        self.folio = folio
        self.context = context if context else {}

    def __str__(self):
        return f"{self.date} {self.narrative} {self.debit_amount} {self.credit_amount}"

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from self.as_cols()

    def as_cols(self):
        date_fmt = self.context.get("date_format", "%-m.%-d")
        yield f"[lightyellow]{self.date.strftime(date_fmt)}" if self.date else ""
        yield f"[black]{self.narrative}" if self.narrative else ""
        decimal_format = self.context.get("decimal_format", "10.2f")
        yield (
            f"[blue]{self.debit_amount.__format__(decimal_format)}"
            if self.debit_amount
            else ""
        )
        yield (
            f"[red]{self.credit_amount.__format__(decimal_format)}"
            if self.credit_amount
            else ""
        )
        yield f"[red]{self.balance.__format__(decimal_format)}"
        yield f"[red]{self.balance_type: >2}"


class TEntry:
    """
    represents a single entry in a T-account
    """

    def __init__(self, date, narrative, amount, folio=None, context=None):
        self.date = date
        self.narrative = narrative
        self.amount = amount
        self.folio = folio
        self.context = context if context else {}

    def __str__(self):
        return f"{self.date} {self.narrative} {self.amount}"

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from self.as_cols()

    def as_cols(self):
        date_fmt = self.context.get("date_format", "%-m.%-d")
        yield f"[yellow]{self.date.strftime(date_fmt)}" if self.date else ""
        yield f"[black]{self.narrative}" if self.narrative else ""
        decimal_format = self.context.get("decimal_format", "10.2f")
        yield (f"[blue]{self.amount.__format__(decimal_format)}" if self.amount else "")


class TBDEntry(TEntry):
    """
    represents a single entry in a T-account for a b/d
    """

    def __init__(self, date, amount, folio=None, **kwargs):
        self.narrative = "Bal b/d"
        super().__init__(date, self.narrative, amount, folio, **kwargs)


class TCDEntry(TEntry):
    """
    represents a single entry in a T-account for a c/d
    """

    def __init__(self, date, amount, **kwargs):
        self.narrative = "Bal c/d"
        super().__init__(date, self.narrative, amount, **kwargs)


class TEmpty(TEntry):
    """
    represents an empty row in a T-account
    """

    def __init__(self, date=None, narrative=None, amount=None, **kwargs):
        super().__init__(date, narrative, amount, **kwargs)

    def __rich__(self) -> str:
        return ""

    def as_cols(self):
        yield from [
            "",
            "",
            "",
        ]


class TTotalEntry(TEntry):
    """
    represents a total entry in a T-account
    """

    def __init__(self, date, amount, narrative=None, one_line=False, **kwargs):
        super().__init__(date, narrative, amount, **kwargs)
        self.one_line = one_line

    def __rich__(self) -> str:
        return f"[bold cyan]{self.amount}"

    def as_cols(self):
        decimal_format = self.context.get("decimal_format", "10.2f")
        amount = self.amount.__format__(decimal_format)
        total_len = len(amount.strip()) + 2
        yield from [
            f"",
            "",
            (
                f"[b green]{'='*total_len}[/b green]"
                if self.one_line
                else f"[b green]{'-'*total_len}[/b green]\n[blue]{amount}[/]\n[b green]{'='*total_len}[/b green]"
            ),
        ]


class TRow:
    """
    represents a row in a T-account, pair of entries
    """

    def __init__(self, debit_entry, credit_entry, *args, **kwargs):
        self.debit_entry = debit_entry
        self.credit_entry = credit_entry

    def __str__(self):
        return f"{self.debit_entry} {self.credit_entry}"

    def __repr__(self):
        return f"[{self.debit_entry}, {self.credit_entry}]"
