from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    LessOperation,
    AddOperation,
)
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.strategies import (
    ClosingBalanceStrategy,
    TransactionTotalStrategy,
)

console = Console()


class LiabilitiesNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "liabilities"),
            title=kwargs.pop("title", "Liabilities"),
            label=kwargs.pop("label", "Liabilities"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Income Statement account")
            self.add_child(
                StatementNode(
                    name="Current Liabilities",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                ).add_child(
                    StatementNode(
                        name="Trade Payables",
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        account_type="accounts-payable",
                        operation=AddOperation,
                        meta=NodeMeta(
                            operation=Operation.ADD,
                            show_subtotal=True,
                        ),
                        value_strategy=TransactionTotalStrategy(),
                    )
                )
            )

        for child in self._children.values():
            child.ensure_expanded()
