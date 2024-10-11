from general_ledger.builders import TransactionBuilder
from general_ledger.models import Direction


class IncomeStatement:
    def __init__(
        self,
        ledger,
        date_start,
        date_end,
        **kwargs,
    ):
        self.ledger = ledger
        self.account_set = ledger.coa.account_set
        if not self.ledger:
            raise ValueError("Ledger is required")
        if not date_start:
            raise ValueError("Start date is required")
        self.date_start = date_start
        if not date_end:
            raise ValueError("End date is required")
        self.date_end = date_end

        self.inventory_opening = self.get_opening_inventory()
        self.inventory_closing = self.get_closing_inventory()

        self.purchases_closing = self.get_purchases()

        self.cost_of_goods_sold = self.get_cost_of_goods_sold()

        self.sales = self.get_sales()

        self.gross_profit = self.get_gross_profit()

        self.update_trading_account()
        self.trading_balance = self.ledger.balance_by_slug(
            "trading",
            balance_date=self.date_end,
        )
        self.profit_and_loss = self.ledger.balance_by_slug(
            "profit-and-loss",
            balance_date=self.date_end,
        )

    def get_opening_inventory(self):
        # inventory_balance = self.ledger.inventory_balance()
        inventory_balance = self.ledger.balance_by_type_slug(
            "inventory",
            balance_date=self.date_start,
            balance_at_close=False,
        )
        return inventory_balance

    def get_closing_inventory(self):
        # inventory_balance = self.ledger.inventory_balance()
        inventory_balance = self.ledger.balance_by_type_slug(
            "inventory",
            balance_date=self.date_end,
        )
        return inventory_balance

    def get_purchases(self):
        purchases_balance = self.ledger.balance_by_type_slug(
            "direct-costs",
            balance_date=self.date_end,
        )
        return purchases_balance

    def get_cost_of_goods_sold(self):
        cost_of_goods_sold = (
            self.inventory_opening + self.purchases_closing - self.inventory_closing
        )
        return cost_of_goods_sold

    def get_sales(self):
        sales_balance = self.ledger.balance_by_type_slug(
            "sales",
            balance_date=self.date_end,
        )
        return sales_balance

    def get_gross_profit(self):
        gross_profit = self.sales - self.cost_of_goods_sold
        return gross_profit

    def get_total_revenue(self):
        pass

    # @TODO this would need to close down all of the accounts
    # of the relevant type in the ledger
    def update_trading_account(self):
        sales = self.ledger.coa.account_set.get(
            name="Sales",
            type__slug="sales",
        )
        purchases = self.ledger.coa.account_set.get(
            name="Purchases",
            type__slug="direct-costs",
        )
        inventory = self.ledger.coa.account_set.get(
            name="Inventory",
            type__slug="inventory",
        )
        closing_inventory = self.ledger.coa.account_set.get(
            name="Closing Inventory",
            type__slug="current-asset",
        )
        trading = self.ledger.coa.account_set.get(
            name="Trading",
            type__slug="equity",
        )
        profit_and_loss = self.ledger.coa.account_set.get(
            name="Profit and Loss",
            type__slug="equity",
        )
        lighting = self.ledger.coa.account_set.get(
            name="Lighting Expenses",
            type__slug="overhead",
        )
        rent = self.ledger.coa.account_set.get(
            name="Rent",
            type__slug="overhead",
        )
        general_expenses = self.ledger.coa.account_set.get(
            name="General Expenses",
            type__slug="overhead",
        )
        drawings = self.ledger.coa.account_set.get(
            name="Drawings",
            type__slug="equity",
        )
        capital = self.ledger.coa.account_set.get(
            name="Capital",
            type__slug="equity",
        )
        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        tb.add_entry(sales, self.sales, Direction.DEBIT)
        tb.add_entry(trading, self.sales, Direction.CREDIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        tb.add_entry(closing_inventory, self.inventory_closing, Direction.DEBIT)
        tb.add_entry(trading, self.inventory_closing, Direction.CREDIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        tb.add_entry(purchases, self.purchases_closing, Direction.CREDIT)
        tb.add_entry(trading, self.purchases_closing, Direction.DEBIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        rent_balance = self.ledger.balance_by_slug(
            "rent",
            balance_date=self.date_end,
        )
        tb.add_entry(
            rent,
            rent_balance,
            Direction.CREDIT,
        )
        tb.add_entry(profit_and_loss, rent_balance, Direction.DEBIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        lighting_balance = self.ledger.balance_by_slug(
            "lighting-expenses",
            balance_date=self.date_end,
        )
        tb.add_entry(
            lighting,
            lighting_balance,
            Direction.CREDIT,
        )
        tb.add_entry(profit_and_loss, lighting_balance, Direction.DEBIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        general_expenses_balance = self.ledger.balance_by_slug(
            "general-expenses",
            balance_date=self.date_end,
        )
        tb.add_entry(
            general_expenses,
            general_expenses_balance,
            Direction.CREDIT,
        )
        tb.add_entry(profit_and_loss, general_expenses_balance, Direction.DEBIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Closing Balance",
        )
        tb.set_trans_date("2012-12-31")
        tb.add_entry(profit_and_loss, self.gross_profit, Direction.CREDIT)
        tb.add_entry(trading, self.gross_profit, Direction.DEBIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Update Capital",
        )
        tb.set_trans_date("2012-12-31")
        drawings_balance = (
            self.ledger.balance_by_slug(
                "drawings",
                balance_date=self.date_end,
            )
            * -1
        )

        print(f"drawings_balance: {drawings_balance}")
        tb.add_entry(capital, drawings_balance, Direction.DEBIT)
        tb.add_entry(drawings, drawings_balance, Direction.CREDIT)
        tb.build().post()

        tb = TransactionBuilder(
            ledger=self.ledger,
            description="Update Capital",
        )
        tb.set_trans_date("2012-12-31")
        net_profit_balance = self.ledger.balance_by_slug(
            "profit-and-loss",
            balance_date=self.date_end,
        )
        tb.add_entry(capital, net_profit_balance, Direction.CREDIT)
        tb.add_entry(profit_and_loss, net_profit_balance, Direction.DEBIT)
        tb.build().post()
