from loguru import logger

from general_ledger.statements.meta import (
    NodeMeta,
    Operation,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.cogs import CostOfGoodsSold
from general_ledger.statements.nodes.sales import SalesNode
from general_ledger.statements.strategies import TransactionTotalStrategy


class TradingAccountNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        name = kwargs.pop("name", "trading")
        super().__init__(
            name=name,
            operation=kwargs.pop("operation", AddOperation),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding trading account")
            self.add_child(
                SalesNode(
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                        show_subtotal=False,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                )
            )

            self.add_child(
                StatementNode(
                    name="returns_inward",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=LessOperation,
                    account_type="returns_inward",
                    meta=NodeMeta(operation=Operation.LESS),
                    value_strategy=TransactionTotalStrategy(),
                )
            )

            self.add_child(
                CostOfGoodsSold(
                    name="cogs",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=LessOperation,
                    meta=NodeMeta(
                        operation=Operation.LESS,
                        label_override="Cost of goods sold:",
                        show_subtotal=True,
                    ),
                )
            )
            for child in self._children.values():
                child.ensure_expanded()

    # def __rich_console__(
    #     self, console: Console, options: ConsoleOptions
    # ) -> RenderResult:
    #     yield f"[b]Account Summary:[/b] #{self.name}"
    #     my_table = Table("Account", "details", "totals")
    #     my_table.add_row("name", str(self.provider))
    #     for child in self._children.values():
    #         my_table.add_row("name", str(child.name))
    #         my_table.add_row("age", str(self.value_strategy))
    #
    #     yield my_table
