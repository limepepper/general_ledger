from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List

from general_ledger.django.models import Account


class AccountingStrategy(ABC):
    """Strategy pattern for different accounting methods"""

    @abstractmethod
    def calculate_sales(
        self, ledger, accounts: List["Account"], start_date: date, end_date: date
    ) -> Decimal:
        pass


class PeriodicAccounting(AccountingStrategy):
    """Calculate figures using periodic accounting method"""

    def calculate_sales(
        self, ledger, accounts: List["Account"], start_date: date, end_date: date
    ) -> Decimal:
        """Calculate sales as difference between closing and opening balances"""
        opening_balance = ledger.balance_for_accounts(
            accounts, balance_date=start_date, balance_at_close=False
        )
        closing_balance = ledger.balance_for_accounts(
            accounts, balance_date=end_date, balance_at_close=True
        )
        return closing_balance - opening_balance


class PerpetualAccounting(AccountingStrategy):
    """Calculate figures using perpetual accounting method"""

    def calculate_sales(
        self, ledger, accounts: List["Account"], start_date: date, end_date: date
    ) -> Decimal:
        """Calculate sales as sum of transactions in period"""
        return ledger.sum_transactions_for_accounts(
            accounts, start_date=start_date, end_date=end_date
        )
