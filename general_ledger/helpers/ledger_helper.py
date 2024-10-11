import itertools
import logging
from rich import inspect
from rich.pretty import pprint
from colorama import Fore, Style, Back

from django.db import transaction
from django.db.models import CharField
from django.db.models import DecimalField
from django.db.models import Q
from django.db.models import Sum, Count
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce
from django.utils import timezone

from general_ledger import constants
from general_ledger.models import Direction
from general_ledger.models.transaction import Transaction
from general_ledger.models.transaction_entry import Entry
from general_ledger.models.account import Account
from general_ledger.models.ledger import Ledger
from general_ledger.utils.account_balanced import AccountBalancer
from general_ledger.utils.consoler import pr_account_balanced


class LedgerHelper:

    logger = logging.getLogger(__name__)

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def get_ledger(self):

        return self.ledger

    def get_ledger_name(self):
        return self.ledger.name

    def get_ledger_book(self):
        return self.ledger.book

    def transfer(self, from_account: Account, to_account: Account, amount: float):
        """
        this basically creates a transaction between two accounts
        but ensures that the transaction is a positive amount. Has a check
        for the appropriate account type and should be 2 single entries
        :param from_account:
        :param to_account:
        :param amount:
        :return:
        """
        assert (
            from_account.ledger == to_account.ledger
        ), "Accounts must be in the same book"
        assert amount > 0, "Amount must be positive"
        # assert (
        #     from_account.ledger.book == self.ledger.book
        # ), "Account must be in the same book as the ledger"
        # assert (
        #     to_account.ledger.book == self.ledger.book
        # ), "Account must be in the same book as the ledger"
        assert from_account != to_account, "From and to accounts must be different"

        if from_account.account_type == constants.TxType.DEBIT:
            from_entry = Entry(
                account=from_account,
                amount=amount,
                tx_type=constants.TxType.CREDIT,
            )
        else:
            from_entry = Entry(
                account=from_account,
                amount=amount,
                tx_type=constants.TxType.DEBIT,
            )

        if to_account.account_type == constants.TxType.DEBIT:
            to_entry = Entry(
                account=to_account,
                amount=amount,
                tx_type=constants.TxType.DEBIT,
            )
        else:
            to_entry = Entry(
                account=to_account,
                amount=amount,
                tx_type=constants.TxType.CREDIT,
            )

        from_entry.save()
        to_entry.save()

    @transaction.atomic
    def build_transaction(self, description: str, entries: list):
        """
        This method builds a transaction from a list of entries
        :param description:
        :param entries:
        :return:
        """
        tx: Transaction = None

        # try:
        with transaction.atomic():
            tx = Transaction(
                ledger=self.ledger,
                description=description,
                post_date=timezone.now(),
            )
            if tx is not None:
                tx.save()
            else:
                raise Exception("Transaction not created")

            models_to_create = []
            for entry in entries:
                models_to_create.append(
                    Entry(
                        account=Account.objects.get(
                            code=entry["account"],
                            coa=self.ledger.coa,
                        ),
                        amount=entry["amount"],
                        tx_type=entry["tx_type"],
                        transaction=tx,
                    )
                )
            Entry.objects.bulk_create(models_to_create)

        return tx
        # except Exception as e:
        #     # Handle exception if needed
        #     print(f"Error: {e}")
        #     return None

    @classmethod
    @transaction.atomic
    def get_account_balance(cls, account: Account):
        cr = Entry.objects.filter(
            account=account,
            tx_type=Direction.CREDIT,
        ).aggregate(
            total=Coalesce(
                Sum(
                    "amount",
                ),
                0.0,
                output_field=DecimalField(),
            ),
        )["total"]
        db = Entry.objects.filter(
            account=account,
            tx_type=Direction.DEBIT,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            ),
        )["total"]
        cls.logger.debug(f"cr: {cr} db: {db}")
        return db - cr

    def get_account_summary(self):
        output = ""
        for account in Account.objects.annotate(num_txs=Count("entry")).filter(
            num_txs__gt=0, coa__ledger=self.ledger
        ):
            balanced = AccountBalancer(
                account=account,
                ledger=self.ledger,
            )
            output = pr_account_balanced(balanced.grouped_entries)
        return output

    def get_entry_summary(self, entryset, account):

        years = sorted(list(set([entry.trans_date.year for entry in entryset])))
        debits = entryset.filter(tx_type=Direction.DEBIT)
        creditz = entryset.filter(tx_type=Direction.CREDIT)

        output = ""
        for year in years:
            debits1 = entryset.filter(
                tx_type=Direction.DEBIT,
                transaction__trans_date__year=year,
            )
            creditz1 = entryset.filter(
                tx_type=Direction.CREDIT,
                transaction__trans_date__year=year,
            )
            zipped = list(itertools.zip_longest(debits1, creditz1, fillvalue=None))
            if len(zipped) == 0:
                continue
            # self.logger.info(f"year: {year} account: {account}")
            output += self.get_year_header_row(year, account, debits1, creditz1)

            # print(len(zipped))
            # print(f"type of zipped: {type(zipped)}")
            for e in zipped:
                # print(f"type of e: {type(e)}")
                # print(f"type of e[0]: {type(e[0])}")
                output += f"{self.get_entry_row(e[0])}|{self.get_entry_row(e[1])}\n"

            # output += self.get_totals_row(account)

        return output

    def get_year_header_row(self, year, account, debits1, creditz1) -> str:
        output = ""
        if len(debits1) and len(creditz1):
            output += f" {Style.BRIGHT}{Fore.CYAN}{year: <31}{Style.RESET_ALL} {account.currency_symbol.center(6)} | {Style.BRIGHT}{Fore.CYAN}{year: <28}{Style.RESET_ALL} {account.currency_symbol.center(10): >10}\n"
        elif len(debits1):
            output += f" {Style.BRIGHT}{Fore.CYAN}{year: <31}{Style.RESET_ALL} {account.currency_symbol.center(6): >6} | {' '*39}\n"
        elif len(creditz1):
            output += f" {' '*38} | {Style.BRIGHT}{Fore.CYAN}{year: <28}{Style.RESET_ALL} {account.currency_symbol.center(10): >10}\n"
        return output

    def get_entry_row(self, entry):
        # print(type(entry))
        output = ""
        if entry:
            # print(self.get_counter_entry(entry))
            tmp = entry.get_counter_entry()
            # print(f"tmp: '{tmp}'")
            output += f" {entry.transaction.trans_date.strftime('%b %e'): <8}{tmp: <19} {entry.amount : >10.2f} "
        else:
            output += f" {' '*38} "
        return output

    def get_totals_row(self, account):
        output = ""
        output += f" {'------'.rjust(38)} | {'-------'.rjust(38)}\n"
        output += f" {'totals'.rjust(38)} | {'1234.00'.rjust(38)}\n"
        output += f" {'======'.rjust(38)} | {'======='.rjust(38)}\n"
        return output
