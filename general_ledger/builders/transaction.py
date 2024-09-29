from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from django.db import transaction
from django.utils import timezone

from general_ledger.models import Account, Transaction, Ledger, Entry, Direction

import logging


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


class TransactionBuilder(TransactionBuilderAbstract):

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        ledger: Ledger = None,
        description: str = "",
    ):
        self.tx = Transaction(
            ledger=ledger,
            description=description,
        )
        self.entries: List[Entry] = []

    def reset(self):
        self.tx = Transaction()
        self.entries = []

    def add_entry(
        self,
        account: Account,
        amount: Decimal,
        tx_type: str,
    ):
        entry = Entry(
            account=account,
            amount=amount,
            tx_type=tx_type,
            transaction=self.tx,
        )
        self.entries.append(entry)

    def set_description(self, description: str):
        self.tx.description = description

    def set_ledger(self, ledger: Account):
        self.tx.ledger = ledger

    def set_trans_date(self, trans_date: timezone):
        self.tx.trans_date = trans_date

    @transaction.atomic
    def build(self) -> Transaction:
        with transaction.atomic():
            bals = {}
            accts = set()
            for entry in self.entries:
                bals[entry.account.pk] = {"CREDITS": 0, "DEBITS": 0}
                accts.add(entry.account.pk)

            for entry in self.entries:
                self.logger.debug(entry.tx_type)
                if entry.tx_type == Direction.CREDIT:
                    bals[entry.account.pk]["CREDITS"] += entry.amount
                elif entry.tx_type == Direction.DEBIT:
                    bals[entry.account.pk]["DEBITS"] += entry.amount
                else:
                    raise Exception(f"Invalid tx_type {entry.tx_type}")

            # self.logger.info(bals)
            if self.tx is not None:
                self.tx.save()
            else:
                raise Exception("Transaction not saved")
            Entry.objects.bulk_create(self.entries)
        return self.tx
