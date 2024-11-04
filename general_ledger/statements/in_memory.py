from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional
from typing import Union

from loguru import logger
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table

import rich.repr
from general_ledger.statements.core_domain import (
    AccountInfo,
    AccountBalance,
    TransactionTotal,
)
from general_ledger.statements.providers import (
    BaseDataProvider,
)


# Example In-Memory Provider for Testing
@dataclass
class InMemoryAccount:
    id: str
    name: str
    account_type: str
    category: str
    balances: Dict[date, Decimal] = field(default_factory=dict)
    transactions: List[tuple[date, Decimal]] = field(default_factory=list)

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.name
        yield "id", self.id
        yield "account_type", self.account_type


class InMemoryProvider(BaseDataProvider):
    """Simple in-memory implementation for testing"""

    def __init__(
        self,
        account_provider=None,
        balance_provider=None,
        transaction_provider=None,
    ):
        self.accounts: Dict[str, InMemoryAccount] = {}
        super().__init__(
            account_provider=account_provider if account_provider else self,
            balance_provider=(balance_provider if balance_provider else self),
            transaction_provider=(
                transaction_provider if transaction_provider else self
            ),
        )  # Self implements all interfaces

    def add_sales(self, id: str) -> "InMemoryAccountBuilder":
        """Quick sales account creation"""
        builder = InMemoryAccountBuilder(id).sales()
        self.accounts[id] = builder.account
        return builder

    def add_account(
        self,
        account: InMemoryAccount,
    ):
        self.accounts[account.id] = account

    # AccountProvider implementation
    def get_account(self, account_id: str) -> Optional[AccountInfo]:
        if account := self.accounts.get(account_id):
            return AccountInfo(
                id=account.id,
                name=account.name,
                account_type=account.account_type,
                category=account.category,
            )
        return None

    def get_accounts_by_type(self, account_type: str) -> List[AccountInfo]:
        return [
            AccountInfo(
                id=str(account.id),
                name=account.name,
                account_type=account.account_type,
                category=account.category,
            )
            for account_id, account in self.accounts.items()
            if account.account_type == account_type
        ]

    def get_balance(
        self, account_id: str, as_of_date: date, at_close: bool = True
    ) -> AccountBalance:
        account = self.accounts.get(account_id)
        if not account:
            return AccountBalance(account_id, Decimal("0.00"), as_of_date)

        balance = account.balances.get(as_of_date, Decimal("0.00"))
        return AccountBalance(account_id, balance, as_of_date)

    def get_balances(
        self, account_ids: list[str], as_of_date: date, at_close: bool = True
    ) -> list[AccountBalance]:
        return [
            self.get_balance(acc_id, as_of_date, at_close) for acc_id in account_ids
        ]

    def get_transaction_total(
        self, account_id: str, start_date: date, end_date: date
    ) -> TransactionTotal:
        account = self.accounts.get(account_id)
        if not account:
            logger.warning(f"got no account for id {account_id}")
            return TransactionTotal(account_id, Decimal("0.00"), start_date, end_date)

        total = sum(
            amount
            for date_, amount in account.transactions
            if start_date <= date_ <= end_date
        )
        # logger.warning(f"returning total  {total} for {account_id}")
        return TransactionTotal(account_id, total, start_date, end_date)

    def get_transaction_totals(
        self,
        account_ids: List[str],
        start_date: date,
        end_date: date,
    ) -> List[TransactionTotal]:
        return [
            self.get_transaction_total(account_id, start_date, end_date)
            for account_id in account_ids
        ]

    def quick_account(self, spec: str) -> None:
        """Parse account spec string:
        "id:type:category|YYYYMMDD:amount|tx:YYYYMMDD:amount"
        """
        parts = spec.split("|")
        id, type_, category = parts[0].split(":")

        account = InMemoryAccount(
            id=id,
            name=f"{id}",
            account_type=type_,
            category=category,
            balances={},
            transactions=[],
        )

        for part in parts[1:]:
            if part.startswith("tx:"):
                _, date_str, amount = part.split(":")
                date_str = date_str.replace("-", "")
                date_ = dt(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
                account.transactions.append((date_, d(amount)))
            else:
                date_str, amount = part.split(":")
                date_str = date_str.replace("-", "")
                date_ = dt(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
                account.balances[date_] = d(amount)

        self.accounts[id] = account

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.__class__.__name__
        yield "accounts", self.accounts, "xx"


class InMemoryProviderBuilder:
    def __init__(self):
        self.provider = InMemoryProvider()

    def with_sales_account(
        self,
        id: str,
        opening: Decimal,
        closing: Decimal,
        transactions: List[tuple[date, Decimal]] = None,
    ) -> "InMemoryProviderBuilder":
        self.provider.add_account(
            InMemoryAccount(
                id=id,
                name=f"Sales Account {id}",
                account_type="sales",
                category="revenue",
                balances={self.start_date: opening, self.end_date: closing},
                transactions=transactions or [],
            )
        )
        return self

    def with_date_range(
        self, start_date: date, end_date: date
    ) -> "InMemoryProviderBuilder":
        self.start_date = start_date
        self.end_date = end_date
        return self

    def build(self) -> InMemoryProvider:
        return self.provider


def d(value: Union[str, int, float]) -> Decimal:
    """Quick Decimal creator"""
    return Decimal(str(value))


def dt(year: int, month: int, day: int) -> date:
    """Quick date creator"""
    return date(year, month, day)


class InMemoryAccountBuilder:
    """Fluent builder for test accounts"""

    def __init__(self, account_id: str):
        self.account = InMemoryAccount(
            id=account_id,
            name=f"{account_id} Account",
            account_type="",
            category="",
            balances={},
            transactions=[],
        )

    def sales(self) -> "InMemoryAccountBuilder":
        """Quick setup for sales account"""
        self.account.account_type = "sales"
        self.account.category = "revenue"
        return self

    def with_type(self, account_type: str) -> "InMemoryAccountBuilder":
        self.account.account_type = account_type
        return self

    def with_category(self, category: str) -> "InMemoryAccountBuilder":
        self.account.category = category
        return self

    def with_name(self, name: str) -> "InMemoryAccountBuilder":
        self.account.name = name
        return self

    def bal(
        self, year: int, month: int, day: int, amount: Union[str, int, float]
    ) -> "InMemoryAccountBuilder":
        """Add balance at date"""
        self.account.balances[dt(year, month, day)] = d(amount)
        return self

    def tx(
        self, year: int, month: int, day: int, amount: Union[str, int, float]
    ) -> "InMemoryAccountBuilder":
        """Add transaction at date"""
        self.account.transactions.append((dt(year, month, day), d(amount)))
        return self

    def build(self) -> InMemoryAccount:
        return self.account
