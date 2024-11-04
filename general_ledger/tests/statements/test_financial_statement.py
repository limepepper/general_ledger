from datetime import date
from decimal import Decimal

from rich.console import Console

from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.format_statement_rich_tree import StatementTreeFormat
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.statements.financial_statement import FinancialStatement
from general_ledger.statements.in_memory import (
    InMemoryProvider,
    InMemoryAccount,
    InMemoryProviderBuilder,
    InMemoryAccountBuilder,
)
from general_ledger.statements.meta import DetailLevel, NodeMeta
from general_ledger.statements.nodes.income_statement import IncomeStatementNode
from general_ledger.statements.nodes.income_statement_corp import (
    IncomeStatementCorpNode,
)
from general_ledger.statements.nodes.profit_and_loss import ProfitAndLossAccount
from general_ledger.statements.nodes.trading_account import TradingAccountNode

console = Console()


class TestFinancialStatement:
    """This is a test class for FinancialStatement"""

    def test_create_statement(self):
        """Test creating a statement"""
        print("")  # for stupid pytest mixing up the console output
        statement = FinancialStatement("Income Statement")
        assert statement.title == "Income Statement"
        assert statement.data == []

        statement.add_row("Sales", ["", "", "38500"])
        statement.add_row("Less Cost of goods sold", ["", "", ""])
        statement.add_row("Purchases", ["", "", "29000"], 1)
        statement.add_row("Closing Inventory", ["", "-3000", ""], 1)
        statement.add_row("Gross Profit", ["", "", "12500"])


#        statement.render()
