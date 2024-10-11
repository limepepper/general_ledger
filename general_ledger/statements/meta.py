from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol


class DetailLevel(Enum):
    VALUE = "value"
    """node returns its own value only"""
    VALUES = "node values"
    """node returns the value of its nodes and its own total"""
    SUMMARY = "summary"
    """node returns its own value and totals from its children"""
    DETAILED = "detailed"
    FULL = "full"
    CHILD = "child"
    """examine child for expand value"""
    EXPAND = "expand"


class Operation(Enum):
    ADD = "+"
    LESS = "-"
    NONE = ""  # For nodes that are just containers/groupings


class NodeOperation(Protocol):
    @staticmethod
    def calculate(node): ...


class AddOperation(NodeOperation):
    @staticmethod
    def calculate(node):
        return node.value


class LessOperation(NodeOperation):
    @staticmethod
    def calculate(node):
        return -node.value


class NoneOperation(NodeOperation):
    @staticmethod
    def calculate(node):
        return node.value


@dataclass
class NodeMeta:
    """Metadata about how a node participates in calculations and display"""

    operation: Operation = Operation.NONE
    indent_level: int = 0
    show_subtotal: bool = False
    label_override: Optional[str] = None
    expand: DetailLevel = DetailLevel.DETAILED
