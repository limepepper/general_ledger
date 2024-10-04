from django.db import models


class BankBalanceType(models.TextChoices):
    """
    Enumeration for different types of bank balances.
    Attributes:
        OPENING (str): Opening balance. One or none, usually entered when bring over from another system.
        CLOSING (str): Closing balance. One or none per bank_account. is associated with a closed account.
        INTERIM (str): Interim balance. Manually entered can be used to find missing transactions.
        STATEMENT (str): Statement balance. recorded during statement import processing.
        EPHEMERAL (str): Ephemeral balance. Used to cache balance calculations for charts.
        UNKNOWN (str): Unknown balance type.
    """

    OPENING = "opening", "Opening"
    CLOSING = "closing", "Closing"
    INTERIM = "interim", "Interim"
    STATEMENT = "statement", "Statement"
    EPHEMERAL = "ephemeral", "Ephemeral"
    OTHER = "other", "Other"
