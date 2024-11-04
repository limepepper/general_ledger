import importlib

import rich.repr
from rich.console import Console
from rich.console import ConsoleOptions, RenderResult
from rich.table import Table

from general_ledger.statements.meta import Operation

statements = importlib.import_module("general_ledger.statements")
# StatementNode = module_node.StatementNode

console = Console()


def __statement_node_rich_repr__(
    node: "statements.node.StatementNode",
) -> rich.repr.Result:
    yield node.name
    yield "start_date", node.start_date, (
        node.parent.start_date if node.parent else None
    )
    yield "end_date", node.end_date, (node.parent.end_date if node.parent else None)
    yield "depth", node.depth, 0
    yield "provider", node.provider, (node.parent.provider if node.parent else "always")
    # yield "path", node.get_path()
    yield "strategy", node.value_strategy.__class__.__name__, (
        node.parent.value_strategy.__class__.__name__ if node.parent else "NoneType"
    )
    yield "account_type", node.account_type, None
    yield "account_id", node.account_id, None
    # this triggers a full calc so can't use rich print in calcs methods unless this is removed, otherwise it will loop
    yield "value", node.value, 0
    yield "sections", node.sections if node.sections.value else None, "NoneType"
    yield "is_visible", node.is_visible, True
    yield "_is_set_visible", node._is_set_visible, None
    yield "expand", node.meta.expand
    yield "children", node._children, {}


def __statement_node_rich_console__(
    node, console: Console, options: ConsoleOptions
) -> RenderResult:
    if node.parent is None:
        my_table = Table(
            "Account", "details", "totals", "egr", "jhigur", "fgrg", expand=True
        )
        for child in node._children.values():
            get_rows(child, my_table)
        my_table.add_row(
            f"{node.name}",
            f"{node.depth:<{node.depth}}",
            "",
            "",
            f"{node.value}",
            "",
        )
        yield my_table


def get_rows(node, table: Table = None) -> None:
    op = node.meta.operation.name
    label = f"{op} {node.name}"
    if node.meta.operation == Operation.LESS and node.has_children:
        table.add_row(f"Less {label}", f"{node.depth:>{node.depth}}", "", "", "", "")
    if node.parent and node.parent.meta.operation == Operation.LESS:
        label = f"   {op} {node.name}"
    for child in node._children.values():
        get_rows(child, table)
    table.add_row(label, f"{node.depth:>{node.depth}}", "", "", "", str(node.value))
