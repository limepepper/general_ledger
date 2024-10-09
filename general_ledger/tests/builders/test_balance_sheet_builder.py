from datetime import datetime, timedelta

import pytest
from rich import inspect

from general_ledger.builders.balance_sheet import BalanceSheetBuilder
from general_ledger.builders.invoice_builder import InvoiceBuilder
from general_ledger.builders.payment import PaymentBuilder
from general_ledger.factories import BookFactory, ContactFactory, BankAccountFactory
from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.helpers.matcher import MatcherHelper
from general_ledger.models import Bank
from general_ledger.models.bank_statement_line_type import BankStatementLineType
from general_ledger.tests.test_chap5 import load_chapter_5_data


class TestBalanceSheetBuilder:

    @pytest.mark.django_db
    def test_simple_balance_sheet_builder(self):
        ledger = load_chapter_5_data()

        builder = BalanceSheetBuilder(
            ledger=ledger,
        )

        balance_sheet = builder.build()

        # inspect(balance_sheet.ledger.coa.account_set.all())
        print(f"all accounts in coa")
        for account in balance_sheet.ledger.coa.account_set.order_by('type__name', 'name'):
            print(account)

        # inspect(balance_sheet.get_non_current_asset_accounts(), title="Non Current Assets")
        print(f"Non Current Asset accounts")
        accounts = balance_sheet.get_non_current_asset_accounts()
        if accounts:
            for account in accounts:
                print(account)
        else:
            print("== No accounts found == ")

        print(f"Current Asset accounts")
        accounts = balance_sheet.get_current_asset_accounts()
        if accounts:
            for account in accounts:
                print(account)
        else:
            print("== No accounts found == ")

        inspect(balance_sheet.get_current_liabilities_accounts(), title="Current Liabilities")
        inspect(balance_sheet.get_non_current_liabilities_accounts(), title="Non Current Liabilities")





    def test_simple_balance_sheet_builder_1(self):
        pass

    def test_simple_balance_sheet_builder_2(self):
        pass
