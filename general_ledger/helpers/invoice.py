"""
Copyright© Put something here

Invoice Helper
_________________

In order to avoid the Invoice model from becoming too large, we have created a helper class to handle the

various operations that can be performed on an invoice. This class will be used to handle the various operations
"""

import logging

from general_ledger.builders import TransactionBuilder
from general_ledger.models import Invoice, Direction

from loguru import logger


class InvoiceHelper:

    logger = logging.getLogger(__name__)

    def __init__(self, pk):
        self.invoice = Invoice.objects.get(pk=pk)

    def do_state_change(self, previous_status, current_status):
        """
        This method is used to handle the state change of an invoice
        :param previous_status: The status of the invoice before the change
        :param current_status: The status of the invoice after the change
        :return:
        """
        logger.info(
            f"Invoice state change {self.invoice.pk} : {previous_status} -> {current_status}"
        )
        if (
            previous_status == Invoice.InvoiceStatus.DRAFT
            and current_status == Invoice.InvoiceStatus.AWAITING_APPROVAL
        ):
            self.create_related_records()
        elif (
            previous_status == Invoice.InvoiceStatus.AWAITING_APPROVAL
            and current_status == Invoice.InvoiceStatus.DRAFT
        ):
            self.delete_related_records()
        elif (
            previous_status == Invoice.InvoiceStatus.AWAITING_APPROVAL
            and current_status == Invoice.InvoiceStatus.AWAITING_PAYMENT
        ):
            self.post_related_records()
        elif (
            previous_status == Invoice.InvoiceStatus.AWAITING_PAYMENT
            and current_status == Invoice.InvoiceStatus.AWAITING_APPROVAL
        ):
            self.unpost_related_records()
        else:
            self.logger.debug(
                f"Invalid state change from {previous_status} to {current_status}"
            )

    def post_related_records(self):
        """
        This method is used to post the related records of an invoice
        during transition from AWAITING_APPROVAL to AWAITING_PAYMENT
        :return:
        """
        for tx in self.invoice.transactions.all():
            if tx.can_post():
                tx.post()
            else:
                self.logger.error(f"Cannot post transaction {tx}")

    def unpost_related_records(self):
        """
        This method is used to unpost the related records of an invoice
        during transition from AWAITING_PAYMENT to AWAITING_APPROVAL
        :return:
        """
        for tx in self.invoice.transactions.all():
            if tx.can_unpost():
                tx.unpost()
            else:
                self.logger.error(f"Cannot unpost transaction {tx}")

    def delete_related_records(self):
        """
        This method is used to delete the related records of an invoice
        during transition from AWAITING_PAYMENT to DRAFT
        :return:
        """
        for tx in self.invoice.transactions.all():
            if tx.can_delete():
                tx.delete()
            else:
                self.logger.error(f"Cannot delete transaction {tx}")

    def create_related_records(self):
        """
        This method is used to create the related records of an invoice
        during transition from DRAFT to AWAITING_APPROVAL
        :return:
        """

        if not self.invoice.sales_account:
            self.invoice.sales_account = self.invoice.get_sales_account()
        if not self.invoice.accounts_receivable:
            self.invoice.accounts_receivable = self.invoice.get_accounts_receivable()
        self.invoice.save()

        tb = TransactionBuilder(
            ledger=self.invoice.ledger,
            description=f"CREATED: invoice {self.invoice.invoice_number}",
        )
        tb.set_trans_date(self.invoice.date)

        tb.add_entry(
            self.invoice.get_accounts_receivable(),
            self.invoice.total_inclusive(),
            Direction.DEBIT,
        )

        tb.add_entry(
            self.invoice.get_sales_account(),
            self.invoice.subtotal(),
            Direction.CREDIT,
        )
        tb.add_entry(
            self.invoice.get_sales_vat_account(),
            self.invoice.total_tax(),
            Direction.CREDIT,
        )
        tx = tb.build()
        assert tx.can_post()

        self.invoice.transactions.add(tx)
        print(f"Created transaction {tx}")
