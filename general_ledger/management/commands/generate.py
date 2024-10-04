import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from loguru import logger
from pygelf import GelfUdpHandler
from rich import inspect
from django.contrib.auth import get_user_model

from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.factories.invoice import InvoiceFactory

from general_ledger.management.utils import (
    get_book,
    get_or_create_customers,
    get_or_create_banks,
)
from general_ledger.models import Bank


class Command(BaseCommand):
    help = "generate Book data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="get this user for use as owner of objects",
            default="admin",
        )
        parser.add_argument(
            "--book",
            type=str,
            help="provide the book to operate on",
        )
        parser.add_argument(
            "--set-demo",
            type=str,
            help="mark the created items as demo objects",
            default=False,
        )
        parser.add_argument(
            "--num-contacts",
            type=int,
            help="num of contacts to get or create",
            default=2,
        )
        parser.add_argument(
            "--num-invoices",
            type=int,
            help="num of invoices to get or create",
            default=5,
        )
        parser.add_argument(
            "--num-banks",
            type=int,
            help="num of checking banks to get or create",
            default=2,
        )

    def handle(self, *args, **kwargs):
        logger.info("===========Generating Financial Data==========")

        user = get_user_model().objects.get(username=kwargs["user"])
        book = get_book(kwargs["book"])
        ledger = book.get_default_ledger()
        is_demo = kwargs["set_demo"]
        num_contacts = kwargs["num_contacts"]
        num_banks = kwargs["num_banks"]
        num_invoices = kwargs["num_invoices"]

        banks = get_or_create_banks(
            book,
            type=Bank.CHECKING,
            num_banks=num_banks,
            is_demo=is_demo,
        )

        customers, _, _ = get_or_create_customers(
            book,
            num_contacts,
            is_demo=is_demo,
        )

        invoice_batch = {}
        for customer in customers:
            invoice_batch[customer] = InvoiceFactory.create_batch(
                num_invoices,
                contact=customer,
                ledger=ledger,
            )

        # randomly record and post invoices for customers
        for customer in customers:
            for invoice in invoice_batch[customer]:
                # @TODO this is dumb as it might cause
                # tests to fail if the invoice is not in the correct state
                # record most of these invoices
                logger.info("recording invoice - maybe")
                if invoice.can_next() and random.uniform(0, 1) > 0.15:
                    logger.info(f"Doing next for {invoice}")
                    invoice.do_next()
                # post most of these invoices
                logger.info("posting invoice - maybe")
                if invoice.can_next() and random.uniform(0, 1) > 0.15:
                    logger.info(f"Doing next for {invoice}")
                    invoice.do_next()

        # randomize generate payments for invoices
        for customer in customers:
            for invoice in invoice_batch[customer]:
                if not invoice.is_posted:
                    continue
                # sometime don't pay invoice
                if random.randint(0, 100) > 95:
                    continue
                dt_skew = random.randint(-15, 20)
                paid_date = invoice.due_date + timedelta(dt_skew)
                # create a memo for the payme
                memo = f"{customer.name.upper()[:18]} {invoice.invoice_number}"
                bank = random.choice(banks)
                tx = BankTransactionFactory.create(
                    bank=bank,
                    amount=invoice.total_inclusive(),
                    date=paid_date,
                    name=memo,
                    type="Direct Debit",
                )

        # ItemFactory.create_batch(10, book=book)
        # book.init_data()
        #
        # bank1 = BankAccountFactory.create(
        #     book=book,
        # )
