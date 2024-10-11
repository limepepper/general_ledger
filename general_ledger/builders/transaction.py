from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional

import rich.repr
from django.db import transaction
from loguru import logger

from general_ledger.django.models.account import Account
from general_ledger.django.models.direction import Direction
from general_ledger.django.models.ledger import Ledger
from general_ledger.django.models.transaction import Transaction
from general_ledger.django.models.transaction_entry import Entry


class TransactionBuilderAbstract(ABC):
    @abstractmethod
    def add_entry(
        self,
        account: Account,
        amount: Decimal,
        tx_type: str,
    ):
        pass

    @abstractmethod
    def build(self) -> Transaction:
        pass


@rich.repr.auto
class TransactionBuilder(TransactionBuilderAbstract):

    def __init__(
        self,
        ledger: Ledger = None,
        description: str = "",
        trans_date: Optional[date] = None,
    ):
        self.trans_date = trans_date
        self.ledger = ledger
        self.description = description
        # @TODO this is dumb. make the tx and entries during build
        self.tx = Transaction(
            ledger=ledger,
            description=description,
            trans_date=trans_date,
        )
        self.entries: List[Entry] = []

    def reset(self):
        self.tx = Transaction()
        self.entries = []

    def add_debit(
        self,
        account: Account,
        amount: Decimal | int | str,
    ):
        return self.add_entry(account, amount, Direction.DEBIT)

    def add_credit(
        self,
        account: Account,
        amount: Decimal | int | str,
    ):
        return self.add_entry(account, amount, Direction.CREDIT)

    def add_entry(
        self,
        account: Account,
        amount: Decimal | int | str,
        tx_type: str,
    ):
        if isinstance(amount, float):
            raise TypeError(
                "The 'amount' parameter cannot be a float. Use Decimal, int, or str instead."
            )

        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(amount)  # Convert to Decimal if needed
            except InvalidOperation as e:
                raise ValueError(
                    "Invalid 'amount' value. It must be convertible to a Decimal. {str(e)}"
                )

        if amount < 0:
            logger.warning(
                "The 'amount' of this entry is negative. account:{} amount:{} type:{}",
                account,
                amount,
                tx_type,
            )

        entry = Entry(
            account=account,
            amount=amount,
            tx_type=tx_type,
            transaction=self.tx,
        )
        self.entries.append(entry)
        return self

    def set_description(self, description: str):
        self.tx.description = description
        return self

    def set_ledger(self, ledger: Account):
        self.tx.ledger = ledger
        return self

    def set_trans_date(self, trans_date: date | datetime | str):
        if isinstance(trans_date, str):
            trans_date = datetime.strptime(trans_date, "%Y-%m-%d").date()

        self.tx.trans_date = trans_date
        return self

    @transaction.atomic
    def build(self) -> Transaction:
        with transaction.atomic():
            bals = {}
            accts = set()
            for entry in self.entries:
                bals[entry.account.pk] = {"CREDITS": 0, "DEBITS": 0}
                accts.add(entry.account.pk)

            for entry in self.entries:
                logger.debug(entry.tx_type)
                if entry.tx_type == Direction.CREDIT:
                    bals[entry.account.pk]["CREDITS"] += entry.amount
                elif entry.tx_type == Direction.DEBIT:
                    bals[entry.account.pk]["DEBITS"] += entry.amount
                else:
                    raise Exception(f"Invalid tx_type {entry.tx_type}")

            # self.logger.info(bals)
            if self.tx is not None:
                # self.tx.trans_date = self.trans_date
                # self.tx.description = self.tx.description
                # self.tx.ledger = self.tx.ledger
                self.tx.save()
            else:
                raise Exception("Transaction not saved")
            Entry.objects.bulk_create(self.entries)
        return self.tx
