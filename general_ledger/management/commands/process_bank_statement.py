from django.core.management.base import BaseCommand
from rich import inspect

from general_ledger.io import ParserFactory
from general_ledger.models import Book, FileUpload, BankStatementLine, Bank, BankBalance
from django.contrib.auth import get_user_model

# from general_ledger.models.account_dl_treebeard import AccountClass


class Command(BaseCommand):
    help = "process bank statement"

    def add_arguments(self, parser):

        parser.add_argument(
            "--file-id",
            type=int,
            help="process a specific file",
        )

    def handle(self, *args, **kwargs):
        user = get_user_model().objects.get(username="admin")
        book = Book.objects.get(name="Demo Company Ltd", owner=user)

        file_upload = FileUpload.objects.get(id=kwargs["file_id"])
        file_path = file_upload.file.path
        parser = ParserFactory.get_parser(file_path)
        parsed_data = parser.parse(file_path)
        # inspect(parsed_data, methods=False)

        bank = Bank.objects.for_book(book).get(
            sort_code=parsed_data["sort_code"],
            account_number=parsed_data["account_number"],
        )

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
