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


class NonCurrentAssets(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "non_current_assets"),
            title=kwargs.pop("title", "Non Current Assets"),
            label=kwargs.pop("label", "Non Current Assets"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Non Current Assets account")
            self.add_child(
                StatementNode(
                    name="Fixtures and Fittings",
                    label="Fixtures",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="non-current-asset",
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                    ),
                    value_strategy=ClosingBalanceStrategy(),
                )
            )

        for child in self.values():
            child.ensure_expanded()
