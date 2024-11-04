from decimal import Decimal

from general_ledger.django.models.account import Account
from general_ledger.django.models.direction import Direction
from general_ledger.django.models.ledger import Ledger
from general_ledger.helpers.ledger_helper import LedgerHelper


def tx(
    ledger: "Ledger",
    dr: "Account",
    amt: Decimal | int | str,
    dt,
    cr: "Account",
    description="Chapter 3.8 data",
):
    """
    convenience function to post a transaction with two entries
    :param ledger:
    :param dr: the account to debit
    :param amt: a Decimal amount
    :param dt: a datetime.date
    :param cr: the account to credit
    :param description:
    :return:
    """
    return LedgerHelper.post_transaction(
        ledger,
        description,
        dt,
        [
            [
                dr,
                amt,
                Direction.DEBIT,
            ],
            [
                cr,
                amt,
                Direction.CREDIT,
            ],
        ],
    )
