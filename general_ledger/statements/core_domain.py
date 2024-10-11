from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol, List, Dict, Optional, Iterator
from enum import Enum


# Core Domain Models
@dataclass(frozen=True)
class AccountBalance:
    """Immutable balance for an account at a point in time"""

    account_id: str
    balance: Decimal
    as_of_date: date


@dataclass(frozen=True)
class TransactionTotal:
    """Immutable total for a set of transactions"""

    account_id: str
    total: Decimal
    start_date: date
    end_date: date


@dataclass(frozen=True)
class AccountInfo:
    """Immutable account information"""

    id: str
    name: str
    account_type: str
    category: str


class AccountingMethod(Enum):
    PERIODIC = "periodic"
    PERPETUAL = "perpetual"
