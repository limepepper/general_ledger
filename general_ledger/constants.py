from enum import Enum

from django.utils.translation import gettext_lazy as _

XERO_ACCT_TYPES_REVERSE = {
    "BANK": "Bank",
    "CURRENT_ASSET": "Current Asset",
    "FIXED_ASSET": "Fixed Asset",
    "INVENTORY": "Inventory",
    "NON_CURRENT_ASSET": "Non-current Asset",
    "PREPAYMENT": "Prepayment",
    "CURRENT_LIABILITY": "Current Liability",
    "LIABILITY": "Liability",
    "NON_CURRENT_LIABILITY": "Non-current Liability",
    # Xero treats Liability and Non-current Liability accounts identically.
    "DEPRECIATION": "Depreciation",
    "DIRECT_COSTS": "Direct Costs",
    "EXPENSE": "Expense",
    "OVERHEAD": "Overhead",
    # Xero treats Expense and Overhead accounts identically.
    "EQUITY": "Equity",
    "OTHER_INCOME": "Other Income",
    "REVENUE": "Revenue",
    "SALES": "Sales",
    # Xero treats Revenue and Sales accounts identically.
}

XERO_ACCT_TYPES = {v: k for k, v in XERO_ACCT_TYPES_REVERSE.items()}

XERO_TYPE_MAP = {
    "Accounts Payable": "Liabilities",
    "Accounts Receivable": "Assets",
    "Bank": "Assets",
    "Current Asset": "Assets",
    "Current Liability": "Liabilities",
    "Depreciation": "Expenses",
    "Direct Costs": "Expenses",
    "Equity": "Equity",
    "Expenses": "Expenses",
    "Fixed Asset": "Assets",
    "Historical": "Equity",
    "Inventory": "Assets",
    "Liability": "Liabilities",
    "Non-Current Asset": "Assets",
    "Non-current Liability": "Liabilities",
    "Other Income": "Revenue",
    "Overhead": "Expenses",
    "Prepayment": "Assets",
    "Retained Earnings": "Liabilities",
    "Revenue": "Revenue",
    "Sales": "Revenue",
    "Rounding": "Equity",
    "Tracking": "Equity",
    "Unpaid Expense Claims": "Liabilities",
    "VAT": "Liabilities",
}

XERO_TYPE_MAP_BASE = {
    "Revenue": "Cr",
    "Liabilities": "Dr",
    "Expenses": "Dr",
    "Assets": "Dr",
    "Equity": "Cr",
}

CREDIT = "credit"
DEBIT = "debit"

TX_TYPE = [(CREDIT, _("Credit")), (DEBIT, _("Debit"))]


class TxType(Enum):
    DEBIT = "Dr"
    CREDIT = "Cr"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
