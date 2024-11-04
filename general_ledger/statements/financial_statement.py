from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, Any
from typing import List

from loguru import logger
from rich.console import Console
from rich.style import Style
from rich.table import Table, Column
from rich.text import Text

from general_ledger.render.mixins.renderable import RenderableMixin
from general_ledger.statements.meta import Operation
from general_ledger.utils.utility import string_to_color
from general_ledger.render.utility_rich import fmt

console = Console()


@dataclass
class FinancialStatement(RenderableMixin):
    """this is just a big tubular dataclass that holds all the data for a financial statement
    each dimension of the statement is a list of dicts, where each dict is a node in the statement
    """

    title: str
    """The title of the statement"""

    data: List[Dict[str, Any]] = field(default_factory=list)
    counts: defaultdict[int, int] = field(default_factory=lambda: defaultdict(int))
    used_columns: defaultdict[int, list] = field(
        default_factory=lambda: defaultdict(list)
    )
    show_op: bool = False
    show_debug: bool = False
    show_type: bool = True

    class Type(Enum):
        NORMAL = "normal"
        TOTAL = "total"
        HEADER = "header"
        LEAF = "leaf"
        SUBTOTAL = "subtotal"
        """a subtotal is the sum if its children"""
        RUNNING = "running"
        """running is subtotal plus prev sibling totals"""
        BLANK = "blank"
        EMPTY = "empty"
        FOOTER = "footer"
        SECTION = "section"
        SUBSECTION = "subsection"

    def add_row(
        self,
        label,
        row: List[Any],
        indent: int = 0,
        node_type: Type = "normal",
        extra=None,
        node=None,
    ):
        if extra is None:
            extra = []
        """Add a row to the statement"""
        if node_type not in [FinancialStatement.Type.FOOTER]:
            self.data.append(
                {
                    "label": label,
                    "cols": row,
                    "indent": indent,
                    "node_type": node_type,
                    "extra": extra,
                    "node": node,
                }
            )
        return self

    # @logger_wraps()
    def add_value(
        self,
        label: str,
        value: Decimal | str,
        col_idx: int = 0,
        indent: int = 0,
        node_type: Type = Type.LEAF,
        extra=None,
        node=None,
    ):

        row: List[Any] = [""] * (col_idx + 1)
        row[col_idx] = value

        # if we are a running, and thw row two above it empty, move it
        # up to the row above it
        # if node_type == self.Type.SUBTOTAL:
        #     if (
        #         self.data[-2]["cols"][col_idx] == ""
        #         and self.data[-1]["cols"][col_idx] == ""
        #         and self.data[-1]["node_type"] == self.Type.RUNNING
        #     ):
        #         # print(f"moving running: {label} {value} to col: {col_idx} {node_type}")
        #         self.data[-2]["cols"][col_idx] = value
        #         return self
        #
        # if node_type == self.Type.RUNNING:
        #     if (
        #         self.data[-1]["cols"][col_idx] == ""
        #         and self.data[-1]["node_type"] == self.Type.RUNNING
        #     ):
        #         # print(
        #         #     f"candiate running: {label} {value} to col: {col_idx} {node_type}"
        #         # )
        #         self.data[-1]["cols"][col_idx] = value
        #         return self

        self.add_row(
            label,
            row,
            indent=indent,
            node_type=node_type,
            extra=extra,
            node=node,
        )
        if node_type not in [FinancialStatement.Type.HEADER]:
            # print(f"add value: {label} {value} to col: {col_idx} {node_type}")
            self.counts[col_idx] += 1
            # self.used_columns[col_idx] = row
        return self

    def render(self):

        if not self.data:
            logger.error("No data to render {}", self.__class__.__name__)
            return

        max_cols = max(len(item["cols"]) for item in self.data)

        table = Table(
            expand=True,
        )

        if self.show_op:
            table.add_column(header="op", vertical="bottom", justify="right")

        table.add_column(
            "label",
            vertical="bottom",
            justify="left",
        )

        if self.show_type:
            table.add_column(
                "type",
                vertical="bottom",
                justify="right",
            )

        # inspect(self.data)
        # print(f"max_cols: {max_cols}")

        for i in range(max_cols - 1, -1, -1):
            table.add_column(vertical="bottom", header=str(i), justify="right")

        if self.show_debug:
            table.add_column(vertical="bottom", header="extra", justify="center")

        for item in self.data:
            extra = item["extra"] if type((item["extra"])) is list else [item["extra"]]
            item["cols"] = [
                *item["cols"],
                *["" for i in range(len(item["cols"]), max_cols)],
            ]
            item["cols"] = list(reversed(item["cols"]))
            row = []
            if self.show_op:
                row.append(item["node"].meta.operation.value)
            row.append(self._fmt_label(item))

            if self.show_type:
                row.append(item["node_type"].value)
            row.extend([self._fmt(item, col) for col in item["cols"]])
            if self.show_debug:
                row.extend([fmt(x) for x in extra])
            table.add_row(*row)
        return table

    def __repr__(self):
        return f"<{self.__class__.__name__}(title='{self.title}',  ({len(self.data)} rows) used_columns: {self.used_columns})>"

    def _fmt_label(self, item):
        bgstyle = string_to_color(item["node"].label)
        indent = "  " * item["indent"]

        style = Style.parse("black") + bgstyle  # Default style

        if item["node"].meta.operation == Operation.NONE:
            label = f"{indent}{item['label']}"
        elif item["node"].meta.operation == Operation.ADD:
            label = f"{indent}{item['node'].meta.operation.value}{item['label']}"
        elif item["node"].meta.operation == Operation.LESS:
            label = f"[italic]LESS[/italic] {item['label']}"
        else:
            raise ValueError(f"Unknown operation: {item['node'].meta}")

        if item["node_type"] == self.Type.TOTAL:
            style = Style.parse("bold black") + bgstyle
            label = label + "\n"
        elif item["node_type"] == self.Type.SUBTOTAL:
            label = "" + label + ""
        elif item["node_type"] in (self.Type.HEADER, self.Type.FOOTER):
            style = Style.parse("dim") + bgstyle
        # No special formatting for LEAF, so it uses the default

        return Text.from_markup(label, style=style)

    def _fmt(self, item, value):
        if item["node_type"] == self.Type.TOTAL and value:
            return fmt(value) + Text("\n======", style="bold")
        elif item["node_type"] == self.Type.SUBTOTAL and value:
            return Text("", style="green") + fmt(value)
        return fmt(value)

    def __rich_repr__(self):
        yield "Title", self.title
        yield "Rows", len(self.data)
        yield "Data", self.data
