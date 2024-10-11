from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from typing import Type

import rich.repr
from loguru import logger
from rich.console import Console
from rich.console import ConsoleOptions, RenderResult

from general_ledger.render.config_statement_render import RenderConfig
from general_ledger.statements.meta import NodeMeta, NodeOperation, NoneOperation
from general_ledger.statements.meta import Operation, DetailLevel
from general_ledger.statements.mixins import TreeMixin
from general_ledger.statements.mixins.rich import (
    __statement_node_rich_repr__,
    __statement_node_rich_console__,
)
from general_ledger.statements.providers import BaseDataProvider
from general_ledger.statements.strategies import ValueStrategy
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.render.mixins.renderable import RenderableMixin


@dataclass
class SectionTotal:
    """Represents the cumulative total for a section of the financial statement."""

    value: Decimal = Decimal(0)
    subtotals: dict[str, Decimal] = field(default_factory=dict)
    first: str = None
    last: str = None

    def add_value(
        self,
        name: str,
        amount: Decimal,
        operation: Operation,
        is_first: bool = False,
        is_last: bool = False,
    ):
        self.first = name if is_first else self.first
        self.last = name if is_last else self.last

        """Add a value to this section's total"""
        modifier = -1 if operation == Operation.LESS else 1
        self.value += amount * modifier

        if name:
            self.subtotals[name] = self.value
        else:
            raise ValueError("SectionTotal.add_value: name must be provided")
