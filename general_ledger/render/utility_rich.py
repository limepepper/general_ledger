import datetime
import random
from collections import defaultdict
from decimal import Decimal
from itertools import zip_longest
from uuid import UUID

from rich import inspect
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

from general_ledger.builders.mixins import StartEndBuilderMixin
from general_ledger.render.mixins.renderable import RenderableMixin
from general_ledger.utils.django import DjangoUtil
from general_ledger.utils.utility import is_iterable
from rich.console import Console

row_styles = [
    Style(
        bgcolor=f"rgb({random.randint(153, 255)}, {random.randint(153, 255)}, {random.randint(153, 255)})"
    )
    for _ in range(20)  # Create 10 random light colors
]


background_styles = [
    Style(
        bgcolor=f"rgb({random.randint(200, 255)}, {random.randint(200, 255)}, {random.randint(200, 255)})"
    )
    for _ in range(40)  # Create 10 random light colors
]


def random_style(target="row"):
    if target == "row":
        return random.choice(row_styles)
    elif target == "col":
        return random.choice(background_styles)
    else:
        raise ValueError("target must be 'row' or 'col'")


def render_any_item(items):
    if isinstance(items, list | tuple):
        return [render_if_possible(item) for item in items]
    return render_if_possible(items)


def render_if_possible(item):
    if isinstance(item, RenderableMixin):
        return item.render()
    return item


# iterate over the
def lists_to_grid_cols(
    *args,
    expand=True,
    random_styles=False,
):
    table = Table.grid(expand=expand)
    col_args = {
        "ratio": 1,
    }
    for _ in args:
        style = random.choice(background_styles) if random_styles else None
        table.add_column(style=style, **col_args)
    args = [arg if is_iterable(arg) else [arg] for arg in args]
    grid = zip_longest(*args, fillvalue=None)
    for row in grid:
        table.add_row(*render_any_item(row))
    return table


def t_account_col_grid() -> tuple[Table, Table]:
    """Create a grid with 3 columns for use in TAccountFormat"""
    for grid in (
        grid1 := Table.grid(expand=True),
        grid2 := Table.grid(
            expand=True,
            pad_edge=False,
        ),
    ):
        grid.add_column(
            justify="left",
            min_width=6,
            # style=random_style("col"),
        )
        grid.add_column(
            justify="left",
            # style=random_style("col"),
        )
        grid.add_column(
            justify="right",
            # style=random_style("col"),
        )
    return grid1, grid2


def model_table_generator(queryset, model):
    table = Table(expand=False)
    fields = DjangoUtil.get_fields(model)
    for field in fields:
        table.add_column(field)
    count = 0
    for item in queryset:
        if count > 20:
            table.add_row("truncated", "...")
            break
        table.add_row(
            *[fmt(getattr(item, field)) for field in fields],
        )
        count += 1
    yield table


def fmt(item, style: str = "cyan", context=None) -> Text:
    """this is a field formatter to allow passing stuff to rich Table row"""
    context = context or {}
    decimal_format = context.get("decimal_format", ">8,.0f")
    date_format = context.get("date_format", "%b  %e")
    if isinstance(item, Decimal):
        if item == 0:
            return Text("", style=style)
        elif item < 0:
            style = "red"
        elif item > 0:
            style = "blue"
        return Text(item.__format__(decimal_format), style=style)
    elif isinstance(item, UUID):
        return Text(str(item), style=style)
    elif isinstance(item, datetime.date):
        return Text(str(item), style="green")
    elif isinstance(item, defaultdict):
        return Text(
            str({k: v for (k, v) in item.items()}).replace(" ", ""), style=style
        )
    else:
        return Text(str(item), style=style)


class ConsoleReportBuilder(
    StartEndBuilderMixin,
):
    def __init__(self, *args, **kwargs):
        """
        Initialize the builder
        """
        self.panel: bool = kwargs.pop("panel", False)
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.context = kwargs
        self.columns: dict[str, list] = defaultdict(list)

    def add_column_item(self, column, item):
        self.columns[column].append(item)
        return self

    def add_column_items(self, column, items):
        for item in items:
            self.add_column_item(column, item)
        return self

    def build(self):
        grid = Table.grid(
            expand=True,
        )
        col_args = {
            "ratio": 1,
        }
        for col, items in self.columns.items():
            grid.add_column(col, **col_args)
        for row in zip_longest(*self.columns.values(), fillvalue=None):
            # inspect(row)
            grid.add_row(
                *[
                    item.render() if isinstance(item, RenderableMixin) else item
                    for item in row
                ]
            )
        if self.panel:
            return Panel(grid)
        return grid
