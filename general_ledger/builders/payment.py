from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from loguru import logger
from rich import print, inspect

from general_ledger.builders.invoice_builder import InvoiceBuilder
from general_ledger.models import (
    Ledger,
    Payment,
    Invoice,
    BankStatementLine,
    DocumentNumberSequence as DocNumSeq,
    Account,
    TaxRate,
)


class PaymentBuilderAbstract(ABC):
    # @abstractmethod
    # def add_entry(
    #     self,
    #     account: Account,
    #     amount: Decimal,
    #     tx_type: str,
    # ):
    #     pass

    @abstractmethod
    def build(self) -> Payment:
        pass


class PaymentBuilder(PaymentBuilderAbstract):
    """
    This class is responsible for building a Payment transaction

    """

    bank_statement_line: BankStatementLine = None
    ledger: Ledger = None
    invoice: Invoice = None

    def __init__(
        self,
        bank_statement_line=None,
        ledger=None,
        description=None,
        **kwargs,
    ):

        self.ledger = ledger
        self.description = description
        self.book = kwargs.get("book")
        self.date = kwargs.get("date", date.today())
        self.kwargs = kwargs
        self.items: list = []
        self.payment: Payment = None
        logger.info(f"{kwargs=} {ledger=} {self.book=}")

    def add_memo_payment(self, **kwargs):
        """
        This method is used to add a very simple explanation
        i.e. one contact, one account, one tax rate, one amount
        :param kwargs:
        :return:
        """
        ib = InvoiceBuilder(
            ledger=self.ledger,
            book=self.ledger.book,
            description=kwargs.get("memo"),
        )
        ib.add_memo_invoice(**kwargs)
        self.invoice = ib.build()

        # payment_item = Payment(
        #     amount=kwargs.get("amount"),
        #     from_object=kwargs.get("bank_statement_line"),
        #     from_account=bank_transaction.bank.id,
        #     to_object=self.invoice,
        #     to_account=self.invoice.get_accounts_receivable(),
        # )

        # payment_item = payment.items.create(
        #     amount=bank_transaction.amount,
        #     from_object=bank_transaction,
        #     from_account=bank_transaction.bank.id,
        #     to_object=invoices[0],
        #     to_account=invoices[0].get_accounts_receivable(),
        # )
        # payment_item.save()

    def add_item(
        self,
        from_object,
        to_object,
    ):
        if from_object.amount != to_object.amount:
            raise ValueError(
                f"Amounts do not match: {from_object.amount=} {to_object.amount=}"
            )

        if isinstance(from_object, Invoice) and not from_object.is_posted:
            raise ValueError("Invoice is not posted")

        if isinstance(to_object, Invoice) and not to_object.is_posted:
            raise ValueError("Invoice is not posted")

        self.items.append(
            {
                "from_object": from_object,
                "to_object": to_object,
            }
        )

    def add_xfer(
        self,
        from_object,
        to_object,
    ):
        if from_object.amount != -to_object.amount:
            raise ValueError(
                f"Amounts do not match: {from_object.amount=} {to_object.amount=}"
            )

        if not isinstance(from_object, BankStatementLine):
            raise ValueError("from account is not bank statement line")

        if not isinstance(to_object, BankStatementLine):
            raise ValueError("to account is not bank statement line")

        self.items.append(
            {
                "from_object": from_object,
                "to_object": to_object,
            }
        )

    def post_invoice(self):
        if self.invoice.is_draft():
            self.invoice.mark_awaiting_approval()
        if self.invoice.is_awaiting_approval():
            self.invoice.mark_approved()

    def build(self) -> Payment:
        self.payment = Payment(
            # amount=bank_transaction.amount,
            date=self.date,
            ledger=self.ledger,
        )
        self.payment.save()
        for item in self.items:
            from_object = item["from_object"]
            to_object = item["to_object"]
            from_account = (
                item["from_object"].bank.account
                if isinstance(from_object, BankStatementLine)
                else item["from_object"].get_accounts_payable()
            )
            to_account = (
                item["to_object"].get_accounts_receivable()
                if isinstance(to_object, Invoice)
                else item["to_object"].bank.account
            )
            payment_item = self.payment.items.create(
                amount=item["from_object"].amount,
                from_object=from_object,
                from_account=from_account,
                to_object=to_object,
                to_account=to_account,
            )
            # payment_item.save()
        return self.payment
