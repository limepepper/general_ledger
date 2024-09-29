import logging
from ofxparse import OfxParser

from general_ledger.models import FileUpload, Bank, Book


class BankStatementHelper:

    logger = logging.getLogger(__name__)

    def __init__(self, file_upload: FileUpload):
        self.file_upload = file_upload

    def process(self):
        with open(self.file_upload.file.path, "r") as fileobj:
            ofx = OfxParser.parse(fileobj)
        account = ofx.account
        if len(account.account_id) == 14:
            sort_code = account.account_id[:6]
            account_number = account.account_id[6:]
        else:
            sort_code = account.routing_number
            account_number = account.account_id

        print(f"{sort_code=}")
        print(f"{account_number=}")

        book = Book.objects.get(name="Demo Company Ltd")

        bank = Bank.objects.for_book(book).get(
            sort_code=sort_code, account_number=account_number
        )

        print(f"{bank=}")

        account = ofx.account
        institution = account.institution
        statement = account.statement

        for transaction in statement.transactions:
            dt = transaction.date
            # conert to year and month

            bank_statement, created = bank.bankstatement_set.get_or_create(
                year=dt.year,
                month=dt.month,
                bank=bank,
            )

            print(f"bank_statement {created=}")
            print(f"======>>>>>")
            print(f"{transaction.type}")
            print(transaction.date)
            print(transaction.date.year)
            print(transaction.date.month)
            print(type(transaction.date))
            print(f"{transaction.user_date=}")
            print(f"{transaction.amount=}")
            print(f"{transaction.payee}")
            print(f"{transaction.memo}")
            print(f"{transaction.id}")

            bank_statement_line = bank_statement.bankstatementline_set.get_or_create(
                bank_statement=bank_statement,
                date=transaction.date,
                amount=transaction.amount,
                payee=transaction.payee,
                memo=transaction.memo,
                transaction_id=transaction.id,
            )
