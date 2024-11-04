from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import Operation, NodeMeta
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.profit_and_loss import ProfitAndLossAccount
from general_ledger.statements.nodes.trading_account import TradingAccountNode

console = Console()


class IncomeStatementNode(
    StatementNode,
):
    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "income"),
            title=kwargs.pop("title", "Income Statement"),
            label=kwargs.pop("label", "Net Profit"),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        if not self._children:
            # Add main components
            logger.trace("Expanding Income Statement account")
            self.add_child(
                TradingAccountNode(
                    label="Gross Profit",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                )
            )
            self.add_child(
                ProfitAndLossAccount(
                    label="Other Activities",
                    name="other-activities",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=True,
                    ),
                )
            )
        for child in self._children.values():
            child.ensure_expanded()
