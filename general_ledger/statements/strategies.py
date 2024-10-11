from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Protocol, List

from loguru import logger

from general_ledger.django.models import Account


class ValueStrategy(Protocol):
    def calculate(self, node: "StatementNode") -> Decimal: ...


class OpeningBalanceStrategy:
    def calculate(self, node: "StatementNode") -> Decimal:
        accounts = node.provider.get_accounts_by_type(node.account_type)
        result = Decimal(
            sum(
                node.provider.get_balance(
                    acc.id, node.start_date, at_close=False
                ).balance
                for acc in accounts
            )
        )
        return result


class ClosingBalanceStrategy:
    def calculate(self, node: "StatementNode") -> Decimal:
        logger.trace(f"Calculating ClosingBalanceStrategy for {node!r}")
        """Calculate closing balance total for a node based on account_id if available"""
        if node.account_id:
            # Calculate for specific account
            logger.trace(f"calculating for specific name {node.account_id}")
            return Decimal(
                node.provider.get_balance(
                    node.account_id,
                    node.end_date,
                    at_close=True,
                ).balance
            )
        elif node.account_type:
            accounts = node.provider.get_accounts_by_type(node.account_type)
            return Decimal(
                sum(
                    node.provider.get_balance(
                        acc.id, node.end_date, at_close=True
                    ).balance
                    for acc in accounts
                )
            )
        raise ValueError(
            f"No account_id or account_type provided for calculation - '{node}'"
        )


class TransactionTotalStrategy:
    def calculate(self, node: "StatementNode") -> Decimal:
        # inspect(node)
        logger.trace(f"Calculating transaction total for {node!r}")
        """Calculate transaction total for a node based on account_id if available"""
        if node.account_id:
            # Calculate for specific account
            logger.trace(f"calculating for specific name {node.account_id}")
            return Decimal(
                node.provider.get_transaction_total(
                    node.account_id, node.start_date, node.end_date
                ).total
            )
        elif node.account_type:
            # Fallback to type-based calculation
            accounts = node.provider.get_accounts_by_type(node.account_type)
            return Decimal(
                sum(
                    node.provider.get_transaction_total(
                        acc.id, node.start_date, node.end_date
                    ).total
                    for acc in accounts
                )
            )
        raise ValueError(
            f"No account_id or account_type provided for calculation - '{node}'"
        )
