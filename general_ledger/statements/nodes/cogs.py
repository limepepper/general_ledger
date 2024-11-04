from loguru import logger

from general_ledger.statements.meta import AddOperation, LessOperation
from general_ledger.statements.statement_node import (
    StatementNode,
    NodeMeta,
    Operation,
)
from general_ledger.statements.strategies import (
    OpeningBalanceStrategy,
    TransactionTotalStrategy,
    ClosingBalanceStrategy,
)


class CostOfGoodsSold(StatementNode):
    def _expand_for_calculation(self) -> None:
        if not self._children:
            logger.trace("Expanding COGS account")
            self.add_child(
                StatementNode(
                    name="opening_inv",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="inventory",
                    value_strategy=OpeningBalanceStrategy(),
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
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
                    operation=AddOperation,
                    value_strategy=TransactionTotalStrategy(),
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                )
            )

            self.add_child(
                StatementNode(
                    name="Purchases Returns",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="purchases-returns",
                    operation=AddOperation,
                    value_strategy=TransactionTotalStrategy(),
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                )
            )

            self.add_child(
                StatementNode(
                    name="closing_inv",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="inventory",
                    operation=LessOperation,
                    value_strategy=ClosingBalanceStrategy(),
                    meta=NodeMeta(
                        operation=Operation.LESS,
                        show_subtotal=True,
                    ),
                )
            )
            for child in self._children.values():
                child.ensure_expanded()
