from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from loguru import logger
from rich import inspect

from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.helpers.matcher import MatcherHelper
from general_ledger.management.utils import (
    get_book,
    get_or_create_banks,
)
from general_ledger.models import Bank, BankStatementLine, Payment, PaymentItem

from django.db.models import Q

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
        parser.add_argument(
            "--bank1",
            type=str,
            help="if operation involves bank to bank transfers, provide the first bank",
            default="",
        )
        parser.add_argument(
            "--bank2",
            type=str,
            help="if operation involves bank to bank transfers, provide the second bank",
            default="",
        )

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.bank2 = None
        self.bank1 = None
        self.num_banks = None
        self.num_contacts = None
        self.is_demo = None
        self.book = None
        self.ledger = None

    def handle(self, *args, **kwargs):
        logger.info("===========Generating Financial Data==========")

        self.user = get_user_model().objects.get(username=kwargs["user"])
        self.book = get_book(kwargs["book"])
        self.ledger = self.book.get_default_ledger()
        self.is_demo = kwargs["set_demo"]
        self.num_contacts = kwargs["num_contacts"]
        self.num_banks = kwargs["num_banks"]

        if kwargs.get("bank1"):
            self.bank1 = Bank.objects.search(kwargs.get("bank1"))
        if kwargs.get("bank2"):
            self.bank2 = Bank.objects.search(kwargs.get("bank2"))

        self.other1()


    def other1(self, *args, **kwargs):

        checking_banks = get_or_create_banks(
            self.book,
            type=Bank.CHECKING,
            num_banks=2,
            is_demo=self.is_demo,
        )

        savings_banks = get_or_create_banks(
            self.book,
            type=Bank.SAVINGS,
            num_banks=2,
            is_demo=self.is_demo,
        )

        # for foo in checking_banks:
        #     inspect(foo)

        # txferss = BankTransactionFactory.create_transfers(
        #     list(checking_banks.all()) + list(savings_banks.all()),
        #     50,
        # )

        txs = BankTransactionFactory.create_batch(
            20,
            bank=self.bank1,
        )
