from general_ledger.statements.statement_node import StatementNode


from loguru import logger

from general_ledger.statements.statement_node import (
    StatementNode,
    DetailLevel,
    NodeMeta,
    Operation,
)
from general_ledger.statements.strategies import (
    OpeningBalanceStrategy,
    TransactionTotalStrategy,
    ClosingBalanceStrategy,
)


class CostOfSalesNode(StatementNode):
    """Node representing aggregate cost of sales figures"""

    def _expand_for_calculation(self) -> None:
        if not self._children:
            logger.trace("Expanding COGS account")
            self.add_child(
                StatementNode(
                    name="opening_inventory",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="inventory",
                    value_strategy=OpeningBalanceStrategy(),
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        indent_level=1,
                    ),
                )
            )

            self.add_child(
                StatementNode(
                    name="purchases",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="purchases",
                    value_strategy=TransactionTotalStrategy(),
                    meta=NodeMeta(operation=Operation.ADD, indent_level=1),
                )
            )

            self.add_child(
                StatementNode(
                    name="closing_inventory",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="inventory",
                    value_strategy=ClosingBalanceStrategy(),
                    meta=NodeMeta(operation=Operation.LESS, indent_level=1),
                )
            )
            for child in self._children.values():
                child.ensure_expanded()
