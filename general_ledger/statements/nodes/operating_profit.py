from loguru import logger

from general_ledger.statements.meta import Operation, NodeMeta, AddOperation
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.expenses import ExpensesNode
from general_ledger.statements.strategies import TransactionTotalStrategy


class OperatingProfit(
    StatementNode,
):

    def __init__(self, **kwargs):
        name = kwargs.pop("name", "Operating Profit")
        super().__init__(
            name=name,
            operation=kwargs.pop("operation", AddOperation),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Operating Profit")
            self.add_child(
                StatementNode(
                    name="Other Operating Income",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="other-income",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            )
            self.add_child(
                ExpensesNode(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    meta=NodeMeta(
                        operation=Operation.LESS,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            )

        for child in self._children.values():
            child.ensure_expanded()
