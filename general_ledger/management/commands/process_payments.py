import sys
from decimal import Decimal

from django.core.management.base import BaseCommand
from loguru import logger
from rich import inspect

from general_ledger.builders.payment import PaymentBuilder
from general_ledger.factories import ContactFactory, BankAccountFactory
from general_ledger.models import Book

logger.add(
    sys.stderr,
    level="TRACE",
    colorize=True,
    format="<level>{time:HH:mm:ss}</level> | <level>{level}</level> | {message} | {extra}",
)


class Command(BaseCommand):
    help = "generate sample banks"

    def handle(self, *args, **kwargs):
        logger.trace("handle in command")

        book = Book.objects.first()
        book.initialize()

        ledger = book.get_default_ledger()
        contact = ContactFactory.customer(book=book)
        (bank_account, account) = BankAccountFactory(book=book)

        pb = PaymentBuilder(
            description="Simple Receive money payment",
            book=book,
            ledger=ledger,
        )

        pb.add_memo_invoice(
            bank_account=bank_account,
            contact=contact,
            description="Receive a payment for a service",
            unit_price=Decimal(100.0000),
            sales_account__slug="sales",
            tax_rate__slug="no-vat",
        )

        # @TODO this should be in invoice builder
        pb.post_invoice()

        # payment = pb.build()
