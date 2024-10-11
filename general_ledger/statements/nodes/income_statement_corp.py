from loguru import logger
from rich.console import Console

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.nodes.operating_profit import OperatingProfit
from general_ledger.statements.nodes.trading_account import TradingAccountNode
from general_ledger.statements.strategies import TransactionTotalStrategy

console = Console()


class IncomeStatementCorpNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name="Statement of Comprehensive Income",
            label="Profit for the financial year",
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
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
                OperatingProfit(
                    name="Operating Profit",
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
                StatementNode(
                    name="Profit before Taxation",
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
                .add_child(
                    StatementNode(
                        name="Interest Receivable",
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        account_type="interest-income",
                        operation=AddOperation,
                        meta=NodeMeta(
                            operation=Operation.ADD,
                            show_subtotal=True,
                        ),
                        value_strategy=TransactionTotalStrategy(),
                    )
                )
                .add_child(
                    StatementNode(
                        name="Disposals",
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        account_type="disposals",
                        operation=AddOperation,
                        meta=NodeMeta(
                            operation=Operation.ADD,
                            show_subtotal=True,
                        ),
                        value_strategy=TransactionTotalStrategy(),
                    )
                )
            )
            self.add_child(
                StatementNode(
                    name="Tax on Profit",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_id="taxstuff",
                    operation=LessOperation,
                    meta=NodeMeta(
                        operation=Operation.LESS,
                        show_subtotal=True,
                    ),
                    value_strategy=TransactionTotalStrategy(),
                ).add_child(
                    StatementNode(
                        name="Corporation Tax",
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        account_type="tax",
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
