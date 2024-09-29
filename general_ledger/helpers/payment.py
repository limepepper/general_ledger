"""
Copyright© Put something here

Payment Helper
_________________

In order to avoid the Payment model from becoming too large, we have created a helper class to handle the

various operations that can be performed on a Payment. This class will be used to handle the various operations
"""

import logging
from loguru import logger
from rich import inspect

from general_ledger.builders import TransactionBuilder
from general_ledger.models import Direction
from general_ledger.models.document_status import DocumentStatus


class PaymentHelper:

    logger = logging.getLogger(__name__)

    def __init__(self, payment):
        self.payment = payment

    def create_related_records(self):
        """
        This method is used to create related records of a payment
        :return:
        """
        tb = TransactionBuilder(
            ledger=self.payment.ledger,
            description=f"CREATED: Payment {self.payment.name}",
        )
        tb.set_trans_date(self.payment.date)

        for line in self.payment.items.all():
            inspect(line.from_object)

            tb.add_entry(
                line.to_account,
                line.amount,
                Direction.DEBIT,
            )

            tb.add_entry(
                line.from_account,
                line.amount,
                Direction.CREDIT,
            )

        tx = tb.build()
        self.payment.transactions.add(tx)

    def post_related_records(self):
        """
        This method is used to post the related records of an payment
        during transition from RECORD to POSTED
        :return:
        """
        for tx in self.payment.transactions.all():
            if tx.can_post():
                tx.post()
            else:
                self.logger.error(f"Cannot post transaction {tx}")

    def reconcile_related_records(self):
        for line in self.payment.items.all():
            line.from_object.reconcile()
            line.to_object.reconcile()

    def unpost_related_records(self):
        """
        This method is used to unpost the related records of an payment
        during transition from POSTED to RECORDED
        :return:
        """
        for tx in self.payment.transactions.all():
            if tx.can_unpost():
                tx.unpost()
            else:
                self.logger.error(f"Cannot unpost transaction {tx}")

    def delete_related_records(self):
        for tx in self.payment.transactions.all():
            if tx.can_delete():
                tx.delete()
            else:
                self.logger.error(f"Cannot delete transaction {tx}")
                raise Exception(f"Cannot delete transaction {tx}")
