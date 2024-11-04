import os
import sys
from decimal import Decimal
from rich import box

sys.path.insert(0, os.getcwd())

import datetime
from rich.table import Table
from rich.style import Style
from rich.console import Console
import random

from general_ledger.render.renderables import TEntry

minA = 240
maxA = 255
minB = 110
maxB = 140

row_styles = [
    Style(bgcolor=f"rgb({r}, {g}, {b})")
    for r, g, b in [
        (
            (
                random.randint(minB, maxB),
                random.randint(minA, maxA),
                random.randint(minA, maxA),
            )
            if i == 0
            else (
                (
                    random.randint(minA, maxA),
                    random.randint(minB, maxB),
                    random.randint(minA, maxA),
                )
                if i == 1
                else (
                    random.randint(minA, maxA),
                    random.randint(minA, maxA),
                    random.randint(minB, maxB),
                )
            )
        )
        for i in [random.choice([0, 1, 2]) for _ in range(20)]
    ]
]


deb1 = TEntry(
    date=datetime.datetime.now(),
    narrative="some narrative",
    amount=Decimal("543.45"),
)


def main():
    console = Console()

    table = Table(
        title="Debit col",
        expand=True,
        show_header=False,
        box=box.MINIMAL_DOUBLE_HEAD,
    )

    table.add_column("date col", justify="left")
    table.add_column("narrative col", justify="left")
    table.add_column("amount", justify="right")

    table.add_row(
        *deb1.as_cols(),
        style=random.choice(row_styles),
    )
    # table.add_row("2022-01-01", "Sales")
    table.add_section()
    table.add_section()
    table.add_section()

    table.add_row(
        "some date",
        "narrative",
        "djfgro",
        style=random.choice(row_styles),
    )

    console.print(table)
    # inspect(table)


if __name__ == "__main__":
    main()
