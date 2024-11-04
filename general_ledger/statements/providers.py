from decimal import Decimal
from typing import Protocol, Dict
from datetime import date
from typing import Optional, List
from typing import Protocol

import rich.repr

from general_ledger.statements.core_domain import (
    AccountInfo,
    AccountBalance,
    TransactionTotal,
)
from general_ledger.statements.meta import NodeMeta, Operation
from general_ledger.statements.strategies import TransactionTotalStrategy


# Data Access Interfaces
class AccountProvider(Protocol):
    """Interface for accessing account information"""

    def get_account(self, account_id: str) -> Optional[AccountInfo]: ...

    def get_accounts_by_type(self, account_type: str) -> List[AccountInfo]: ...


class BalanceProvider(Protocol):
    """Interface for accessing account balances"""

    def get_balance(
        self, account_id: str, as_of_date: date, at_close: bool = True
    ) -> AccountBalance: ...

    def get_balances(
        self, account_ids: List[str], as_of_date: date, at_close: bool = True
    ) -> List[AccountBalance]: ...


class TransactionProvider(Protocol):
    """Interface for accessing transaction information"""

    def get_transaction_total(
        self, account_id: str, start_date: date, end_date: date
    ) -> TransactionTotal: ...

    def get_transaction_totals(
        self, account_ids: List[str], start_date: date, end_date: date
    ) -> List[TransactionTotal]: ...


class BaseDataProvider:
    """Combines all provider interfaces with default implementations"""

    def __init__(
        self,
        account_provider: AccountProvider,
        balance_provider: BalanceProvider,
        transaction_provider: TransactionProvider,
    ):
        self.account_provider = account_provider
        self.balance_provider = balance_provider
        self.transaction_provider = transaction_provider

    def __rich_repr__(self) -> rich.repr.Result:
        yield "account_provider", self.account_provider
        yield "balance_provider", self.balance_provider
        yield "transaction_provider", self.transaction_provider


class CachingProviderDecorator(BaseDataProvider):
    def __init__(
        self,
        provider: BaseDataProvider,
        account_provider: AccountProvider,
        balance_provider: BalanceProvider,
        transaction_provider: TransactionProvider,
    ):
        super().__init__(account_provider, balance_provider, transaction_provider)
        self.provider = provider
        self._cache = {}

    def get_balance(
        self, account_id: str, as_of_date: date, at_close: bool = True
    ) -> AccountBalance:
        cache_key = (account_id, as_of_date, at_close)
        if cache_key not in self._cache:
            self._cache[cache_key] = self.provider.get_balance(
                account_id, as_of_date, at_close
            )
        return self._cache[cache_key]


class LoggingProviderDecorator(BaseDataProvider):
    def __init__(
        self,
        provider: BaseDataProvider,
        logger,
        account_provider: AccountProvider,
        balance_provider: BalanceProvider,
        transaction_provider: TransactionProvider,
    ):
        super().__init__(account_provider, balance_provider, transaction_provider)
        self.provider = provider
        self.logger = logger

    def get_balance(
        self, account_id: str, as_of_date: date, at_close: bool = True
    ) -> AccountBalance:
        self.logger.debug(f"Getting balance for {account_id} at {as_of_date}")
        result = self.provider.get_balance(account_id, as_of_date, at_close)
        self.logger.debug(f"Balance is {result.balance}")
        return result


# Example usage with test provider
class TestProvider(BaseDataProvider):
    def get_accounts_by_type(self, account_type: str) -> List[AccountInfo]:
        if account_type == "overhead":
            return [
                AccountInfo(
                    id="rent-exp",
                    name="Rent Expense",
                    account_type="overhead",
                    category="expense",
                ),
                AccountInfo(
                    id="util-exp",
                    name="Utilities Expense",
                    account_type="overhead",
                    category="expense",
                ),
                AccountInfo(
                    id="sal-exp",
                    name="Salaries and Wages",
                    account_type="overhead",
                    category="expense",
                ),
            ]
        return []

    def get_transaction_total(
        self, account_id: str, start_date: date, end_date: date
    ) -> TransactionTotal:
        # Example transactions for specific accounts
        totals = {
            "rent-exp": Decimal("8000"),
            "util-exp": Decimal("4000"),
            "sal-exp": Decimal("8000"),
        }
        return TransactionTotal(
            account_id=account_id,
            total=totals.get(account_id, Decimal("0")),
            start_date=start_date,
            end_date=end_date,
        )
