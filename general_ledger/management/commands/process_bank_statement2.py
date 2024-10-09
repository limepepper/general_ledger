from django.core.management.base import BaseCommand
from rich import inspect

from general_ledger.helpers.routing_number_lookup import create_sort_code_trie
from general_ledger.helpers.sort_code_lookup import sort_codes
from general_ledger.io import ParserFactory
from general_ledger.management.utils import get_book
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
            "--book",
            type=str,
            help="provide the book to operate on",
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
        self.book = get_book(kwargs["book"])

        if not self.book:
            logger.error("Book not found")
            return

        file_upload = FileUpload.objects.get(id=kwargs["file_id"])
        file_path = file_upload.file.path
        parser = ParserFactory.get_parser(file_path)
        parsed_data = parser.parse(file_path)

        # inspect(parsed_data, methods=False)

        # bank = Bank.objects.for_book(book).get(
        #     sort_code=parsed_data["sort_code"],
        #     account_number=parsed_data["account_number"],
        # )

        for account in  parsed_data["accounts"]:
            print(f"{account['balance']=}")
            print(f"{account['balance_date']=}")
            print(f"{account['sort_code']=}")
            print(f"{account['account_number']=}")

            inspect(account)

            trie = create_sort_code_trie(sort_codes)


            print(trie.lookup("60-24-77"))

            inspect(self.book.bank_set.all())

            try:
                bank = self.book.bank_set.get(
                    sort_code=account["sort_code"],
                    account_number=account["account_number"],
                )
            except Bank.DoesNotExist as e:
                bank_name = trie.lookup(account["sort_code"])
                print(f"{bank_name=}")

                if account["account_type"] == "CHECKING":
                    account_suffix = "Current Account"
                    account_type = Bank.CHECKING
                elif account["account_type"] == "SAVINGS":
                    account_suffix = "Savings Account"
                    account_type = Bank.SAVINGS
                else:
                    account_suffix = "Account"
                    account_type = Bank.CHECKING

                bank = Bank.objects.create_with_account(
                    book=self.book,
                    sort_code=account["sort_code"],
                    account_number=account["account_number"],
                    name=f"{bank_name} {account_suffix}",
                    type=account_type,
                )


        # if not parsed_data["transactions"]:
        #     print("No transactions found")
        #     return
        #
        # print(f"{parsed_data['sort_code']=}")
        # print(f"{parsed_data['account_number']=}")

        # for data in parsed_data["transactions"]:
        #     inspect(data)
