import uuid

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from loguru import logger
import pytz

from general_ledger.helpers.bank_balance_helper import BankBalanceHelper
from general_ledger.models import BankBalance, Bank


class Command(BaseCommand):
    help = "generate balances data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--bank1",
            type=str,
            help="if operation involves bank to bank transfers, provide the first bank",
            default="",
        )

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.bank1 = None
        self.bank2 = None
        self.num_banks = None
        self.num_contacts = None
        self.is_demo = None
        self.book = None
        self.ledger = None

    def handle(self, *args, **kwargs):
        if kwargs.get("bank1"):
            self.bank1 = Bank.objects.search(kwargs.get("bank1"))
        if kwargs.get("bank2"):
            self.bank2 = Bank.objects.search(kwargs.get("bank2"))

        logger.info("===========Generating Financial Data==========")
        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         """
        #         SELECT date, bank_id, SUM(amount) OVER (PARTITION BY bank_id ORDER BY date) as running_balance
        #         FROM gl_bank_statement_line
        #         ORDER BY bank_id, date;
        #     """
        #     )
        #
        #     rows = cursor.fetchall()

        bbh = BankBalanceHelper(self.bank1)
        balance = bbh.get_balance()


        self.stdout.write(self.style.SUCCESS("Successfully inserted running balances"))
