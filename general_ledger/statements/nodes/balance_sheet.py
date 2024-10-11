from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.nodes.assets import AssetsNode
from general_ledger.statements.nodes.liabilities import LiabilitiesNode
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.profit_and_loss import ProfitAndLossAccount
from general_ledger.statements.nodes.trading_account import TradingAccountNode
from general_ledger.statements.strategies import (
    TransactionTotalStrategy,
    ClosingBalanceStrategy,
)

console = Console()


class BalanceSheetNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "balance_sheet"),
            title=kwargs.pop("title", "Balance Sheet"),
            label=kwargs.pop("label", "Balance sheet"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Balance Sheet account")
            self.add_child(
                AssetsNode(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                )
            )
            self.add_child(
                LiabilitiesNode(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=LessOperation,
                    meta=NodeMeta(
                        operation=Operation.LESS,
                        show_subtotal=True,
                    ),
                )
            )

        for child in self.values():
            child.ensure_expanded()
