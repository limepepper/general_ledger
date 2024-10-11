from decimal import Decimal

import pytest
from django.template.loader import get_template
from rich import inspect

# from rich import print
from rich.console import Console

from general_ledger.builders.income_statement import IncomeStatementBuilder
from general_ledger.helpers import LedgerHelper
from general_ledger.models import Account
from general_ledger.tests.book.test_chap7 import load_exhibit_7_1

console = Console()


class TestIncomeStatementBuilder:

    @pytest.mark.django_db
    def test_simple_income_statement_builder_1(self):

        ledger = load_exhibit_7_1()

        assert ledger.balance_by_type_slug("sales") == Decimal("38500")
        assert ledger.balance_by_type_slug("overhead") == Decimal("4500")
        assert ledger.balance_by_type_slug("inventory") == Decimal("3000.00")
        assert ledger.balance_by_type_slug(
            "inventory",
            balance_date="2012-11-30",
        ) == Decimal("0.00")

    @pytest.mark.django_db
    def test_simple_income_statement_builder_2(self):

        ledger = load_exhibit_7_1()

        builder = IncomeStatementBuilder(
            ledger=ledger,
            start_date="2012-12-01",
            end_date="2012-12-31",
        )

        income_statement = builder.build()

        # lh = LedgerHelper(ledger)
        # print(lh.get_account_summary())

        template = get_template("gl/console/three_col_accounts.j2")

        context = {
            "ledger": ledger,
            "accounts": Account.objects.filter(coa=ledger.coa),
        }

        # self.logger.info(template.render(context=context))

        print(template.render(context=context))

        inspect(income_statement)

        # inspect(ledger)

        # ac = AccountContext(cash)
        # self.logger.info(ac.get_context_report())
