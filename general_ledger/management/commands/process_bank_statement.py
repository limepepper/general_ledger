from django.core.management.base import BaseCommand
from rich import inspect

from general_ledger.io import ParserFactory
from general_ledger.models import Book, FileUpload, BankStatementLine, Bank, BankBalance
from django.contrib.auth import get_user_model
from loguru import logger
# from general_ledger.models.account_dl_treebeard import AccountClass


class Command(BaseCommand):
    help = "process bank statement"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.bank1 = None

    def add_arguments(self, parser):

        parser.add_argument(
            "--file-id",
            type=int,
            help="process a specific file",
        )
        parser.add_argument(
            "--bank1",
            type=str,
            help="if operation involves bank to bank transfers, provide the first bank",
            default="",
        )

    def handle(self, *args, **kwargs):
        logger.info("===========bank statement==========")

        if kwargs.get("bank1"):
            self.bank1 = Bank.objects.search(kwargs.get("bank1"))

        file_upload = FileUpload.objects.get(id=kwargs["file_id"])
        file_path = file_upload.file.path
        parser = ParserFactory.get_parser(file_path)
        parsed_data = parser.parse(file_path)

        # inspect(parsed_data, methods=False)

        # bank = Bank.objects.for_book(book).get(
        #     sort_code=parsed_data["sort_code"],
        #     account_number=parsed_data["account_number"],
        # )

        if "balance" in parsed_data and "balance_date" in parsed_data:
            print(f"{parsed_data['balance']=}")
            print(f"{parsed_data['balance_date']=}")
            balance, created = BankBalance.objects.get_or_create(
                bank=bank,
                balance=parsed_data["balance"],
                balance_date=parsed_data["balance_date"],
                balance_source=parsed_data["balance_source"],
            )

        if not parsed_data["transactions"]:
            print("No transactions found")
            return

        print(f"{parsed_data['sort_code']=}")
        print(f"{parsed_data['account_number']=}")

        for data in parsed_data["transactions"]:
            line, created = BankStatementLine.objects.get_or_create(
                bank=bank,
                hash=data["hash"],
                date=data["date"],
                amount=data["amount"],
                defaults=dict(
                    name=data["name"],
                    transaction_id=data["transaction_id"],
                    type=data["type"],
                ),
            )
            if created:
                print(f"created: {line}")
            else:
                print(f"exists: {line}")
