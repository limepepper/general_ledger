from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from general_ledger.render.config_statement_render import RenderConfig
from general_ledger.render.formats_abc import StatementFormat
from general_ledger.render.utility_rich import lists_to_grid_cols
from general_ledger.statements.meta import Operation
from general_ledger.statements.statement_node import StatementNode
from general_ledger.utils.inspect import inspect
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


class StatementTableFormatReverse(StatementFormat):
    def __init__(self):
        super().__init__()
        self.config_key = "statement_table_reverse"

    def render_statement(self, renderer, node: StatementNode):
        print("Rendering statement with Rich Table upside down")

        out = node.accept(self.ReverseVisitor(renderer=renderer, node=node))

        opts = {
            "show_calculation": renderer.options.get("show_calculation", False),
            "show_hidden": renderer.options.get("show_hidden", False),
        }

        items = []
        items.append(Text("something here"))

        result = lists_to_grid_cols(items)
        renderer.renderable = result
        return result

    class ReverseVisitor(RecursiveFuncVisitor):
        def __init__(self, **kwargs):
            super().__init__(pre_func=self._pre_func, post_func=self._post_func)
            self.current_level = 0
            self.options = kwargs.get("options")
            self.reverse = True

        def _pre_func(self, visitee, _):
            indent = "->" * visitee.depth
            return f"pre :{indent} {visitee.title:18.18} {visitee.name:18.18} {visitee.label}"

        def _post_func(self, visitee, _):
            indent = "->" * visitee.depth
            return f"post :{indent} {visitee.title:18.18} {visitee.name:18.18} {visitee.label}"
            

