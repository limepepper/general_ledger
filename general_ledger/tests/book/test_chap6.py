import pytest
from loguru import logger
from rich import inspect

from general_ledger.helpers import LedgerHelper
from general_ledger.tests.book.test_chap3 import load_chapter_3_data
from general_ledger.utils.account_balanced import AccountBalancer
from general_ledger.utils.account_t_format import AccountTAccount
from general_ledger.utils.consoler import pr_account_list


def load_chapter_6_data():

    ledger = load_chapter_3_data()
    return ledger


class TestChapter6TrialBalance:
    """
    trial balance stuff
    """

    @pytest.mark.django_db
    def test_chap6_show_balanced_accounts(self):
        ledger = load_chapter_6_data()

        lh = LedgerHelper(ledger)
        print(lh.get_account_summary())

        purchases = ledger.coa.account_set.get(name="Purchases")

        print(
            pr_account_list(
                ledger,
                ledger.coa.account_set.all(),
                title="account report",
            )
        )

        test = AccountBalancer(
            ledger,
            purchases,
        )
        inspect(test)

        test2 = AccountBalancer(
            ledger,
            purchases,
            "2013-05-09",
        )

        inspect(test2)
        # ata = AccountTAccount(
        #     test2.account.name,
        #     "ref",
        #     test2.debit_rows,
        #     test2.credit_rows,
        # )
        # print(ata.report())
        #
        # inspect(ledger.coa.account_set.all())

        # test3 = AccountBalanced(
        #     ledger,
        #     purchases,
        #     end_date="2013-05-09",
        # )
        # inspect(test3)
