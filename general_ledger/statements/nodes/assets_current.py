from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.nodes.liabilities import LiabilitiesNode
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.profit_and_loss import ProfitAndLossAccount
from general_ledger.statements.nodes.trading_account import TradingAccountNode
from general_ledger.statements.strategies import (
    TransactionTotalStrategy,
    ClosingBalanceStrategy,
)

console = Console()


class CurrentAssets(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "current_assets"),
            title=kwargs.pop("title", "Current Assets"),
            label=kwargs.pop("label", "Current Assets"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Non Current Assets account")
            self.add_child(
                StatementNode(
                    name="inventory",
                    label="Inventory",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="inventory",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                    ),
                    value_strategy=ClosingBalanceStrategy(),
                )
            ).add_child(
                StatementNode(
                    name="Bank Account",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="bank",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            ).add_child(
                StatementNode(
                    name="Cash",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="cash",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            ).add_child(
                StatementNode(
                    name="Trade Receivables",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="accounts-receivable",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            )

        for child in self.values():
            child.ensure_expanded()
