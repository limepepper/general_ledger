from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.nodes.assets_current import CurrentAssets
from general_ledger.statements.nodes.liabilities import LiabilitiesNode
from general_ledger.statements.nodes.assets_non_current import NonCurrentAssets
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.profit_and_loss import ProfitAndLossAccount
from general_ledger.statements.nodes.trading_account import TradingAccountNode
from general_ledger.statements.strategies import (
    TransactionTotalStrategy,
    ClosingBalanceStrategy,
)

console = Console()


class AssetsNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "assets"),
            title=kwargs.pop("title", "Assets"),
            label=kwargs.pop("label", "Assets"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Assets Node")
            self.add_child(
                NonCurrentAssets(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                    ),
                )
            )

            self.add_child(
                CurrentAssets(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                    ),
                )
            )

        for child in self.values():
            child.ensure_expanded()
