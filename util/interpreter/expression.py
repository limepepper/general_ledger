#
#
#
from typing import Protocol, Dict, Any


class Expression(Protocol):
    def interpret(self, context: Dict[Any, Any]) -> Any: ...


class TerminalExpression(Expression): ...


class NonTerminalExpression(Expression): ...
