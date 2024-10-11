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
from general_ledger.statements.mixins import TreeMixin, StartEndMixin
from general_ledger.statements.mixins.rich import (
    __statement_node_rich_repr__,
    __statement_node_rich_console__,
)
from general_ledger.statements.providers import BaseDataProvider
from general_ledger.statements.statement_section import SectionTotal
from general_ledger.statements.strategies import ValueStrategy
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.render.mixins.renderable import RenderableMixin
from general_ledger.utils.utility import raiseu, logger_wraps, logger_init


class StatementNode(
    StartEndMixin,
    TreeMixin["StatementNode"],
    RenderableMixin,
):
    """Hierarchical node in a financial statement"""

    # @logger_init()
    def __init__(
        self,
        /,
        name: str,
        *,
        provider: BaseDataProvider,
        title: str = None,
        meta: Optional[NodeMeta] = None,
        operation: Type[NodeOperation] = None,
        value_strategy: Optional[ValueStrategy] = None,
        account_type: str = None,
        account_id: str = None,
        label=None,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.detail_level = None
        self.label: str = label if label else self.name
        self.title: str = title if title else self.name
        self.provider = provider
        self.meta = meta or NodeMeta()
        self.account_type = account_type
        self.account_id = account_id  # Store account_id
        self._value: Optional[Decimal] = None
        self.value_strategy = value_strategy
        self._is_expanded = False
        self._is_visible = True
        self._is_set_visible = None
        # these are both attempts to track the running total in siblings
        # which kind of indicate a conceptual error in the design
        self.accumulated_value = Decimal("0")
        self.sections: SectionTotal = SectionTotal()
        self.operation = operation or NoneOperation

    @property
    def value(self) -> Decimal:
        """Get the value for this node"""
        if self._value is None:
            self._value = self.calculate()
        return self._value

    def is_effectively_zero(self, config: RenderConfig) -> bool:
        """Check if node's value is effectively zero"""
        return abs(self.value) < config.materiality_threshold

    def is_empty_branch(self, config: RenderConfig) -> bool:
        """
        Check if this node and all its descendants are empty
        """
        if not self.is_effectively_zero(config):
            return False

        return all(child.is_empty_branch(config) for child in self.values())

    def prune_empty(self):
        """Prune empty branches from this node"""
        for child in list(self.values()):
            if child.is_empty_branch(RenderConfig()):
                del self[child.name]
        for child in self.values():
            child.prune_empty()
        return self

    def should_be_visible(self, config: RenderConfig) -> bool:
        """Determine if node should be visible based on all criteria"""
        if not self.is_visible:
            return False

        if config.hide_empty and self.is_empty_branch(config):
            return False

        return True

    @property
    def is_visible(self) -> bool:
        """True if this node is visible"""
        return (
            self._is_set_visible
            if self._is_set_visible is not None
            else self._is_visible
        )

    def calculate(self) -> Decimal:
        """Calculate value including operation sign"""
        self.ensure_expanded()

        if self.has_children:
            running_total = Decimal("0")
            for i, child in enumerate(self.values()):
                running_total += child.operation.calculate(child)
                child.accumulated_value = running_total
                self.sections.add_value(
                    child.name,
                    child.value,
                    child.meta.operation,
                    is_first=i == 0,
                    is_last=i == len(self) - 1,
                )

            result = running_total
        elif self.value_strategy:
            result = self.value_strategy.calculate(self)
        else:
            raise ValueError(f"Node is leaf but has no value strategy  '{self!r}'")

        return result

    def ensure_expanded(self) -> "StatementNode":
        """Ensures node is expanded for calculation purposes"""
        if not self._is_expanded:
            self._expand_for_calculation()
            self._is_expanded = True
        return self

    def _expand_for_calculation(self) -> None:
        """Internal method to expand node for calculation"""
        # Override in subclasses to add necessary child nodes
        pass

    def set_expand(self, detail_level: DetailLevel) -> "StatementNode":
        """Controls which nodes are expanded based on detail level"""
        self.meta.expand = detail_level
        for child in self.values():
            child.set_expand(detail_level)
        return self

    def set_visibility(self, detail_level: DetailLevel) -> "StatementNode":
        """Controls which nodes are visible based on detail level"""
        if detail_level == DetailLevel.SUMMARY:
            # Only show top-level nodes
            self._is_visible = not self.parent
        elif detail_level == DetailLevel.DETAILED:
            # Show up to second level
            self._is_visible = not self.parent or not self.parent.parent
        else:  # FULL
            self._is_visible = True

        for child in self.values():
            child.set_visibility(detail_level)
        return self

    def render(self):
        if not self.renderer:
            logger.trace("No renderer set, using default StatementRenderer")
            self.renderer = StatementRenderer()
        return super().render()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name if hasattr(self, 'name') else 'None'})"

    def __rich_repr__(self) -> rich.repr.Result:
        yield from __statement_node_rich_repr__(self)

    __rich_repr__.angular = True

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from __statement_node_rich_console__(self, console, options)
