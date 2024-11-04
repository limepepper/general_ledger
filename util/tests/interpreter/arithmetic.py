from typing import Dict, Any

from util.interpreter.expression import (
    NonTerminalExpression,
    Expression,
    TerminalExpression,
)

#
#
#


class Integer(TerminalExpression):
    def __init__(self, value: int) -> None:
        self._value = value

    def interpret(self, context: Dict[Any, Any]) -> int:
        return self._value

    def __repr__(self):
        return str(self._value)


class Add(NonTerminalExpression):
    def __init__(
        self,
        left: Expression,
        right: Expression,
    ) -> None:
        self._left = left
        self._right = right

    def interpret(
        self,
        context: Dict[Any, Any],
    ) -> Any:
        return self._left.interpret(context) + self._right.interpret(context)

    def __repr__(self):
        return f"({self._left} Add {self._right})"


class Subtract(Expression):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def interpret(self, context):
        return self._left.interpret(context) - self._right.interpret(context)

    def __repr__(self):
        return f"({self._left} Subtract {self._right})"


class Multiply(NonTerminalExpression):
    def __init__(
        self,
        left: Expression,
        right: Expression,
    ) -> None:
        self._left = left
        self._right = right

    def interpret(
        self,
        context: Dict[Any, Any],
    ) -> Any:
        return self._left.interpret(context) * self._right.interpret(context)

    def __repr__(self):
        return f"({self._left} Times {self._right})"


class Divide(NonTerminalExpression):
    def __init__(
        self,
        left: Expression,
        right: Expression,
    ) -> None:
        self._left = left
        self._right = right

    def interpret(
        self,
        context: Dict[Any, Any],
    ) -> Any:
        return self._left.interpret(context) // self._right.interpret(context)
