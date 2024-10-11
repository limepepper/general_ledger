from datetime import date
from datetime import date
from typing import List, Optional

from general_ledger.django.models import Account
from general_ledger.statements.core_domain import (
    AccountInfo,
    TransactionTotal,
    AccountBalance,
)
from general_ledger.statements.ledger_account import LedgerAccount
from general_ledger.statements.providers import BaseDataProvider
from general_ledger.utils.inspect import inspect


# Django ORM Provider
class DjangoProvider(BaseDataProvider):
    """Django ORM implementation"""

    def __init__(self, ledger):
        self.ledger = ledger
        super().__init__(self, self, self)

    def __repr__(self):
        return f"{self.__class__.__name__}(ledger={self.ledger})"

    # AccountProvider implementation
    def get_account(self, account_id: str) -> Optional[AccountInfo]:
        qs = self.ledger.coa.account_set.get_fuzzy(account_id)
        inspect(qs.query)
        inspect(qs)
        account = qs.first()
        if account:
            return AccountInfo(
                id=str(account.id),
                name=account.name,
                account_type=account.type.slug,
                category=account.type.category,
            )
        else:
            raise ValueError(f"Account not found: {account_id}")

    # @logger_wraps(entry=True, exit=True)
    def get_accounts_by_type(self, account_type: str) -> List[AccountInfo]:
        accounts = self.ledger.coa.account_set.filter(type__slug=account_type)
        return [
            AccountInfo(
                id=str(account.id),
                name=account.name,
                account_type=account.type.slug,
                category=account.type.category,
            )
            for account in accounts
        ]

    # @logger_wraps(entry=True, exit=True)
    def get_transaction_total(
        self, account_id: str, start_date: date, end_date: date
    ) -> TransactionTotal:
        ledger_account = LedgerAccount(
            ledger=self.ledger,
            account=Account.objects.get(id=account_id),
        )
        return TransactionTotal(
            account_id, ledger_account.balance, start_date, end_date
        )

    # @logger_wraps(entry=True, exit=True)
    def get_balance(
        self, account_id: str, as_of_date: date, at_close: bool = True
    ) -> AccountBalance:
        ledger_account = LedgerAccount(
            ledger=self.ledger,
            account=Account.objects.get_fuzzy(account_id),
        )
        if at_close:
            balance = ledger_account.all().upto(as_of_date).balance()
        else:
            balance = ledger_account.all().before(as_of_date).balance()

        return AccountBalance(account_id, balance, as_of_date)
