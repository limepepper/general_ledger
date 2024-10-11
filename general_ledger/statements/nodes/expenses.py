from general_ledger.statements.meta import (
    NodeMeta,
    Operation,
    LessOperation,
    AddOperation,
)
from general_ledger.statements.statement_node import StatementNode
from general_ledger.statements.strategies import TransactionTotalStrategy


class ExpensesNode(
    StatementNode,
):

    def __init__(self, **kwargs):
        super().__init__(
            operation=LessOperation,
            name="expenses",
            **kwargs,
        )

    def _expand_for_calculation(self) -> None:
        """Expand trading account into its components"""
        if not self._children:
            expense_accounts = self.provider.get_accounts_by_type("overhead")

            # Sort by name for consistent display
            expense_accounts.sort(key=lambda x: x.name)

            for account in expense_accounts:
                self.add_child(
                    StatementNode(
                        name=account.name,
                        provider=self.provider,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        operation=AddOperation,
                        meta=NodeMeta(
                            operation=Operation.ADD,
                            indent_level=1,
                            show_subtotal=True,
                        ),
                        account_type="overhead",
                        account_id=account.id,
                        value_strategy=TransactionTotalStrategy(),
                    )
                )
