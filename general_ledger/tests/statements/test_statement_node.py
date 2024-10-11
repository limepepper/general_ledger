from datetime import date
from decimal import Decimal

from rich.console import Console

from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.format_statement_rich_tree import StatementTreeFormat
from general_ledger.render.renderer_statement import StatementRenderer
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


def test_inmemory_quickloader():
    # Usage becomes:
    provider = InMemoryProvider()
    provider.quick_account(
        "sales1:sales:revenue|20240101:1000|20241231:5000|tx:20240315:2000|tx:20240701:2000"
    )
    assert provider.get_account("sales1").id == "sales1"


# Usage in tests
def test_sales_calculation():
    provider = (
        InMemoryProviderBuilder()
        .with_date_range(date(2024, 1, 1), date(2024, 12, 31))
        .with_sales_account("SALES1", Decimal("1000"), Decimal("5000"))
        .with_sales_account("SALES2", Decimal("2000"), Decimal("8000"))
        .build()
    )

    # inspect(provider)


# Example Usage and Testing
def test_trading_account():
    print("")
    # Create test data
    provider = InMemoryProvider()

    # Add test accounts
    provider.add_account(
        InMemoryAccount(
            id="sales1",
            name="Product Sales",
            account_type="sales",
            category="revenue",
            transactions=[
                (date(2024, 7, 1), Decimal("38500.00")),
            ],
        )
    )

    provider.add_account(
        InMemoryAccountBuilder("Purchases")
        .with_type("purchases")
        .with_category("asset")
        .tx(2024, 7, 1, 29000)
        .build()
    )

    provider.add_account(
        InMemoryAccountBuilder("Inventory")
        .with_type("inventory")
        .with_category("asset")
        .bal(2024, 1, 1, 0)
        .bal(2024, 12, 31, 3000)
        .build()
    )

    # Create trading account
    trading = TradingAccountNode(
        provider=provider,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        meta=NodeMeta(
            show_subtotal=True,
        ),
    ).ensure_expanded()

    # force build the tree
    # results = trading.render(DetailLevel.DETAILED)
    # console.print(trading)
    # trading._children["cost_of_goods_sold"]._children[
    #     "opening_inventory"
    # ]._is_set_visible = True
    # display_trading_account(trading)
    # console = Console()
    # tree = render_statement_tree(trading, show_calculation=True)
    # tree.guide_style = "bold bright_blue"
    # console.print(tree)

    assert trading.value == Decimal("12500.00")


def test_profit_and_loss_account():
    # Create test data
    provider = InMemoryProvider()
    # provider.add_account(
    #     InMemoryAccountBuilder("Other Income")
    #     .with_type("other-income")
    #     .with_category("revenue")
    #     .tx(2024, 7, 1, 1000)
    #     .build()
    # )

    provider.add_account(
        InMemoryAccountBuilder("Rent")
        .with_type("overhead")
        .with_category("expense")
        .tx(2024, 12, 31, 2400)
        .build()
    )

    provider.add_account(
        InMemoryAccountBuilder("Lighting Expenses")
        .with_type("overhead")
        .with_category("expense")
        .tx(2024, 12, 31, 1500)
        .build()
    )

    provider.add_account(
        InMemoryAccountBuilder("General Expenses")
        .with_type("overhead")
        .with_category("expense")
        .tx(2024, 12, 31, 600)
        .build()
    )

    profit_and_loss = ProfitAndLossAccount(
        provider=provider,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        meta=NodeMeta(
            show_subtotal=True,
        ),
    )

    # profit_and_loss.expand(DetailLevel.FULL)

    # display_trading_account(profit_and_loss)


def test_income_statement_node_0():

    print("")

    provider = InMemoryProvider()

    [
        provider.quick_account(a)
        for a in [
            "sales:sales:revenue|2024-01-01:1000|2024-12-31:5_000|tx:2024-03-01:38_500",
            "purchases:purchases:asset|2024-01-01:1_000|2024-12-31:5000|tx:2024-07-01:29000",
            "Inventory:inventory:asset|20240101:0|20241231:0|20241231:3000",
            "Rent:overhead:expense|20240101:0|20241231:0|tx:20241231:2400",
            "Lighting Expenses:overhead:expense|20240101:0|20241231:0|tx:20241231:1500",
            "General Expenses:overhead:expense|20240101:0|20241231:0|tx:20241231:600",
        ]
    ]

    ic = (
        IncomeStatementNode(
            provider=provider,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            meta=NodeMeta(
                show_subtotal=True,
            ),
            label="Income Statement",
        )
        .ensure_expanded()
        .prune_empty()
    )

    ic.set_renderer(StatementRenderer())
    console.print("\n=== Full View ===")
    ic.set_render_format(
        "statement",
        StatementTreeFormat(),
        detail_level=DetailLevel.FULL,
    ).render()

    console.print("\n=== Detailed View ===")
    ic.set_render_format(
        "statement",
        StatementTreeFormat(),
        detail_level=DetailLevel.DETAILED,
    ).render()

    console.print("\n=== Summary View ===")
    ic.set_render_format(
        "statement",
        StatementTreeFormat(),
        detail_level=DetailLevel.SUMMARY,
    ).render()

    ic.set_renderer(StatementRenderer())
    console.print("\n=== Full View with ValueStrategy label ===")
    ic.set_render_format(
        "statement",
        StatementTreeFormat(),
        detail_level=DetailLevel.FULL,
        show_calculation=True,
    ).render()


def test_income_statement_node_1():

    print("")
    provider = InMemoryProvider()

    [
        provider.quick_account(a)
        for a in [
            # Main revenue/turnover
            "sales:sales:revenue|2023-01-01:0|2023-12-31:0|tx:2023-06-30:44_995_186",
            # Cost of sales components
            "purchases:purchases:asset|2023-01-01:0|2023-12-31:0|tx:2023-06-30:29_938_003",
            "inventory:inventory:asset|2023-01-01:0|2023-12-31:0",  # No inventory movement
            # Administrative expenses
            "admin-expenses:overhead:expense|2023-01-01:0|2023-12-31:0|tx:2023-06-30:10_254_147",
            # Other operating income
            "other-income:other-income:revenue|2023-01-01:0|2023-12-31:0",  # Zero for 2023
            # Interest income
            "interest-income:interest-income:revenue|2023-01-01:0|2023-12-31:0|tx:2023-06-30:1_464_998",
            # Disposal profit
            "disposal-profit:disposals:revenue|2023-01-01:0|2023-12-31:0|tx:20230630:114_231_109",
            # Tax
            "tax:tax:expense|2023-01-01:0|2023-12-31:0|tx:2023-12-31:1_671_492",
            "tax:tax:expense|2023-01-01:0|2023-12-31:0|tx:2023-12-31:1_671_492",
        ]
    ]

    income_statement = (
        IncomeStatementCorpNode(
            provider=provider,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            meta=NodeMeta(
                show_subtotal=True,
                expand=DetailLevel.SUMMARY,
            ),
        )
        .ensure_expanded()
        .prune_empty()
    )
    # console.print(Pretty(income_statement))
    #
    # income_statement.prune_empty()

    # console.print(Pretty(income_statement))
    # console.print(income_statement)

    income_statement.render()

    # display_trading_account(income_statement)
    # income_statement.build()


def test_income_statement_node_2():

    print("")

    provider = InMemoryProvider()

    [
        provider.quick_account(a)
        for a in [
            "sales:sales:revenue|2024-01-01:1000|2024-12-31:5_000|tx:2024-03-01:38_500",
            "purchases:purchases:asset|2024-01-01:1_000|2024-12-31:5000|tx:2024-07-01:29000",
            "Inventory:inventory:asset|20240101:0|20241231:0|20241231:3000",
            "Rent:overhead:expense|20240101:0|20241231:0|tx:20241231:2400",
            "Lighting Expenses:overhead:expense|20240101:0|20241231:0|tx:20241231:1500",
            "General Expenses:overhead:expense|20240101:0|20241231:0|tx:20241231:600",
        ]
    ]

    ic = (
        IncomeStatementNode(
            provider=provider,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            meta=NodeMeta(
                show_subtotal=True,
            ),
            label="Income Statement",
        )
        .ensure_expanded()
        .prune_empty()
    )

    ic.set_renderer(StatementRenderer())
    console.print("\n=== Full View ===")
    ic.set_render_format(
        "statement",
        StatementFormatRichTable(),
        # detail_level=DetailLevel.FULL,
    ).render()
