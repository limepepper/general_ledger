from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from loguru import logger
from rich import inspect

from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.management.utils import (
    get_book,
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

        checking_banks = get_or_create_banks(
            book,
            type=Bank.CHECKING,
            num_banks=2,
            is_demo=is_demo,
        )

        savings_banks = get_or_create_banks(
            book,
            type=Bank.SAVINGS,
            num_banks=2,
            is_demo=is_demo,
        )

        # for foo in checking_banks:
        #     inspect(foo)

        txferss = BankTransactionFactory.create_transfers(
            list(checking_banks.all()) + list(savings_banks.all()),
            50,
        )

        txs = BankTransactionFactory.create_batch(
            20,
            bank=checking_banks[0],
        )
