from loguru import logger

from general_ledger.statements.meta import (
    Operation,
    NodeMeta,
    AddOperation,
    LessOperation,
)
from general_ledger.statements.nodes.assets_current import CurrentAssets
from general_ledger.statements.nodes.assets_non_current import NonCurrentAssets
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.strategies import ClosingBalanceStrategy


class CapitalNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "Owner's Equity"),
            title=kwargs.pop("title", "Owner's Equity"),
            label=kwargs.pop("label", "total=="),
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            # Add main components
            logger.trace("Expanding Capital Node")

            self.add_child(
                StatementNode(
                    name="Capital",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    operation=AddOperation,
                    meta=NodeMeta(
                        operation=Operation.ADD,
                    ),
                ).add_child(
                    StatementNode(
                        name="Cash introduced",
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        account_id="capital",
                        operation=AddOperation,
                        meta=NodeMeta(
                            operation=Operation.ADD,
                        ),
                        value_strategy=ClosingBalanceStrategy(),
                    )
                )
                # .add_child(
                #     StatementNode(
                #         name="profits",
                #         title="Add Net profit for the year",
                #         provider=self.provider,
                #         start_date=self.start_date,
                #         end_date=self.end_date,
                #         operation=AddOperation,
                #         account_id="capital1",
                #         meta=NodeMeta(
                #             operation=Operation.ADD,
                #         ),
                #         value_strategy=ClosingBalanceStrategy(),
                #     )
                # )
            )

            self.add_child(
                StatementNode(
                    name="Drawings",
                    provider=self.provider,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    account_type="drawings",
                    operation=LessOperation,
                    meta=NodeMeta(
                        operation=Operation.LESS,
                    ),
                    value_strategy=ClosingBalanceStrategy(),
                )
            )

        for child in self.values():
            child.ensure_expanded()
