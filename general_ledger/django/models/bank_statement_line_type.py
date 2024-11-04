from django.db import models


class BankStatementLineType(models.TextChoices):
    """
    Enumeration for different types of bank statement lines.

    Attributes:
        CREDIT (str): Credit transaction.
        DEBIT (str): Debit transaction.
        INT (str): Interest transaction.
        DIV (str): Dividend transaction.
        FEE (str): Fee transaction.
        SRVCHG (str): Service charge transaction.
        DEP (str): Deposit transaction.
        ATM (str): ATM transaction.
        XFER (str): Transfer transaction.
        CHECK (str): Check transaction.
        PAYMENT (str): Payment transaction.
        CASH (str): Cash withdrawal transaction.
        DIRECTDEP (str): Direct deposit transaction.
        DIRECTDEBIT (str): Direct debit transaction.
        REPEATPMT (str): Repeat payment transaction.
        HOLD (str): Hold transaction.
        OTHER (str): Other transaction.
        UNKNOWN (str): Unknown transaction type.
    """

    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"
    INT = "interest", "Interest"
    DIV = "dividend", "Dividend"
    FEE = "fee", "Fee"
    SRVCHG = "service_charge", "Service Charge"
    DEP = "deposit", "Deposit"
    ATM = "atm", "ATM"
    XFER = "transfer", "Transfer"
    CHECK = "check", "Check"
    PAYMENT = "payment", "Payment"
    CASH = "cash", "Cash"
    DIRECTDEP = "direct_deposit", "Direct Deposit"
    DIRECTDEBIT = "direct_debit", "Direct Debit"
    REPEATPMT = "repeat_payment", "Repeat Payment"
    HOLD = "hold", "Hold"
    OTHER = "other", "Other"
    UNKNOWN = "unknown", "Unknown"
