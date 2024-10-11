import pytest
from rich import inspect
from rich import print as rprint

# from rich import print
from rich.console import Console

from general_ledger.builders.balance_sheet import BalanceSheetBuilder
from general_ledger.helpers import LedgerHelper
from general_ledger.models import AccountType, Entry
from general_ledger.tests.book.test_chap5 import load_chapter_5_data
from general_ledger.tests.book.test_chap7 import load_exhibit_7_3, load_exhibit_7_1
from general_ledger.utils.consoler import pr_account_list
from colorama import Back, Style

console = Console()


def get_content(account):
    """Extract text from user dict."""
    name = f"{account.name}"
    type = f"{AccountType.Category(account.type.category)}"
    return f"[b]{name}[/b]\n[yellow]{type}"


class TestBalanceSheetBuilder:

    @pytest.mark.django_db
    def test_simple_balance_sheet_builder_1(self):

        ledger = load_exhibit_7_1()

        builder = BalanceSheetBuilder(
            ledger=ledger,
        )

        lh = LedgerHelper(ledger)
        print(lh.get_account_summary())

        # inspect(ledger)

        # ac = AccountContext(cash)
        # self.logger.info(ac.get_context_report())

        balance_sheet = builder.build()

        # accounts = balance_sheet.ledger.coa.account_set.all()
        # print(pr_account_list(accounts, title="All accounts in COA"))

        accounts_nca = balance_sheet.get_non_current_asset_accounts()
        print(pr_account_list(ledger, accounts_nca, title="Non Current Asset accounts"))

        # Combine the querysets to get only entries in both
        # combined_entries = transaction_entries & account_entries
        combined_entries_nca = Entry.objects.filter(
            transaction__ledger=ledger,
            account__in=accounts_nca,
        )

        # inspect(combined_entries_nca.balance())

        accounts_ca = balance_sheet.get_current_asset_accounts()
        print(pr_account_list(ledger, accounts_ca, title="Current Asset account"))

        # Combine the querysets to get only entries in both
        # combined_entries = transaction_entries & account_entries
        combined_entries_ca = Entry.objects.filter(
            transaction__ledger=ledger,
            account__in=accounts_ca,
        )

        rprint("total assets " + str(combined_entries_nca.balance() + combined_entries_ca.balance()))

        # inspect(combined_entries_ca.balance())

        accounts = balance_sheet.get_current_liabilities_accounts()
        print(pr_account_list(ledger, accounts, title="Current Liability accounts"))

        accounts = balance_sheet.get_non_current_liabilities_accounts()
        print(pr_account_list(ledger, accounts, title="Non Current Liability accounts"))

    @pytest.mark.django_db
    def test_simple_balance_sheet_builder_2(self):

        ledger = load_chapter_5_data()

        builder = BalanceSheetBuilder(
            ledger=ledger,
        )

        lh = LedgerHelper(ledger)
        # print(lh.get_account_summary())

        balance_sheet = builder.build()

        accounts = balance_sheet.ledger.coa.account_set.all()
        print(pr_account_list(ledger, accounts, title="All accounts in COA"))

        # Combine the querysets to get only entries in both
        # combined_entries = transaction_entries & account_entries
        combined_entries = Entry.objects.filter(
            transaction__ledger=ledger,
            account__in=accounts,
        )

        # inspect(combined_entries.balance())

        accounts = balance_sheet.get_non_current_asset_accounts()
        print(pr_account_list(ledger, accounts, title="Non Current Asset accounts"))

        accounts = balance_sheet.get_current_asset_accounts()
        print(pr_account_list(ledger, accounts, title="Current Asset account"))

        accounts = balance_sheet.get_current_liabilities_accounts()
        print(pr_account_list(ledger, accounts, title="Current Liability accounts"))

        # Combine the querysets to get only entries in both
        # combined_entries = transaction_entries & account_entries
        combined_entries = Entry.objects.filter(
            transaction__ledger=ledger,
            account__in=accounts,
        )

        # inspect(combined_entries.balance())

        for foo in combined_entries:
            print(
                f"entry: {Back.LIGHTGREEN_EX}{foo}{Style.RESET_ALL} {Back.YELLOW}{foo.account.name}{Style.RESET_ALL} {foo.transaction}"
            )

        accounts = balance_sheet.get_non_current_liabilities_accounts()
        print(pr_account_list(ledger, accounts, title="Non Current Liability accounts"))

        # Assuming you have a transaction object and a list of account objects
        transaction_entries = Entry.objects.filter(transaction__ledger=ledger)
        print(f"count of transaction_entries: {transaction_entries.count()}")
        account_entries = Entry.objects.filter(account__in=accounts)
        print(f"count of account_entries: {account_entries.count()}")

        # Combine the querysets to get only entries in both
        combined_entries = transaction_entries & account_entries

        for foo in combined_entries:
            print(
                f"entry: {Back.LIGHTGREEN_EX}{foo}{Style.RESET_ALL} {Back.YELLOW}{foo.account.name}{Style.RESET_ALL} {foo.transaction}"
            )
