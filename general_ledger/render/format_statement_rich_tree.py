from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from general_ledger.render.config_statement_render import RenderConfig
from general_ledger.render.formats_abc import StatementFormat
from general_ledger.statements.meta import Operation
from general_ledger.statements.statement_node import StatementNode
from util.visitors.recursive_func import RecursiveFuncVisitor

console = Console()

"""
=== Full View ===
Income Statement 0
├── + Gross Profit 0
│   ├── + Sales 38,500
│   ├── - Returns Inward 0
│   └── - Cost of goods sold: 0
│       ├── + Opening Inventory 0
│       ├── + Purchases 29,000.00
│       └── - Closing Inventory -3,000
└── - Net Profit 0.00
    ├── + Other Operating Income 0
    └── - Expenses 0
        ├── + General Expenses Account 600
        ├── + Lighting Expenses Account 1,500
        └── + Rent Account 2,400
"""


class StatementTreeFormat(StatementFormat):
    def __init__(self):
        super().__init__()
        self.config_key = "statement_tree"

    def render_statement(self, renderer, node):
        print("Rendering statement with Rich Tree")

        node.accept(
            RecursiveFuncVisitor(
                pre_func=lambda visitee, _: visitee.set_visibility(
                    renderer.options.get("detail_level")
                )
            )
        )

        opts = {
            "show_calculation": renderer.options.get("show_calculation", False),
            "show_hidden": renderer.options.get("show_hidden", False),
        }

        result = render_statement_tree(node, **opts)
        renderer.renderable = result
        return result


def render_statement_tree(
    node: StatementNode,
    show_calculation: bool = False,
    show_hidden: bool = False,
    config: RenderConfig = RenderConfig(),
) -> Optional[Tree]:
    """
    Render a statement node as a Rich Tree with optional calculation details.
    Only renders visible nodes and optionally indicates hidden children.
    """

    node.ensure_expanded()

    # Check if node should be visible
    if not node.should_be_visible(config):
        return None

    # Skip if node isn't visible
    if not node.is_visible:
        return None

    # Process children first
    visible_children = []
    has_hidden_children = False
    has_empty_children = False

    for child in node.values():
        if child.is_visible:
            child_tree = render_statement_tree(
                child,
                show_calculation=show_calculation,
                show_hidden=show_hidden,
                config=config,
            )
            if child_tree is not None:
                visible_children.append(child_tree)
            elif config.hide_empty and child.is_empty_branch(config):
                has_empty_children = True
            else:
                has_hidden_children = True
        else:
            # Check if this hidden child has visible descendants
            has_hidden_children = has_hidden_children or any(
                c.is_visible for c in child.values()
            )
            # has_hidden_children = True

    # Build the label for this node
    label_parts = []

    # Operation
    operation = (
        f"{node.meta.operation.value} " if node.meta.operation != Operation.NONE else ""
    )
    label_parts.append(Text(operation, style="blue"))

    # Label
    label = node.meta.label_override or node.label.replace("_", " ").title()
    label_parts.append(Text(label))

    # Value
    if node.is_leaf or node.meta.show_subtotal:
        value_str = f" {node.value:,.{config.decimal_places}f}"
        style = "red" if node.value < 0 else "green"
        label_parts.append(Text(value_str, style=style))

        if show_calculation and node.value_strategy:
            strategy_name = node.value_strategy.__class__.__name__
            label_parts.append(Text(f" ({strategy_name})", style="dim"))

    # Create tree
    tree = Tree(Text.assemble(*label_parts))

    # Add visible children
    for child_tree in visible_children:
        tree.add(child_tree)

    if show_hidden and has_hidden_children and not visible_children:
        hidden_values = sum(
            child.value
            for child in node.values()
            if not child.is_visible and any(c.is_visible for c in child.values())
        )
        tree.add(
            Text(
                f"(... hidden items totaling {hidden_values:,.{config.decimal_places}f})",
                style="dim",
            )
        )

    return tree
