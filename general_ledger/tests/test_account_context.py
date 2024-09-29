import logging
from loguru import logger
from general_ledger import constants
from general_ledger.factories import BookFactory
from general_ledger.helpers import LedgerHelper
from general_ledger.models import (
    Transaction,
    Account,
    Ledger,
    Direction,
    AccountType,
    TaxRate,
)
from general_ledger.reports import AccountContext
from general_ledger.tests import GeneralLedgerBaseTest

from general_ledger.builders import TransactionBuilder


class AccountContextTests(GeneralLedgerBaseTest):

    def test_1(self):
        """
        1. Started a household machines business putting £2 ,000 into a
        bank account.
        """
        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()
        cash = Account.objects.get(name="Cash", coa=coa)
        capital = Account.objects.get(name="Capital", coa=coa)
        bank = Account.objects.get(name="Bank Account", coa=coa)
        savings = Account.objects.get(name="Savings Account", coa=coa)
        accts_receivable = Account.objects.get(name="Accounts Receivable", coa=coa)
        accts_payable = Account.objects.get(name="Accounts Payable", coa=coa)
        computer_software, _ = coa.account_set.get_or_create(
            name="Computer Software",
            type=book.accounttype_set.get(slug="overhead"),
            tax_rate=book.taxrate_set.get_or_create(
                slug="20-vat-on-expenses",
                tax_type=book.taxtype_set.get(slug="purchases"),
            )[0],
        )

        tb = TransactionBuilder(
            ledger=ledger, description="Started a household machines business"
        )

        tb1 = TransactionBuilder(ledger=ledger, description="Test Transaction - 1")
        tb1.set_trans_date("2012-08-1")
        tb1.add_entry(cash, 10_000, Direction.DEBIT)
        tb1.add_entry(capital, 10_000, Direction.CREDIT)
        tx1 = tb1.build()
        self.assertTrue(tx1.can_post())
        tx1.post()
        self.assertEqual(LedgerHelper.get_account_balance(cash), 10_000)

        tb2 = TransactionBuilder(ledger=ledger, description="Test Transaction - 2")
        tb2.set_trans_date("2012-08-2")
        tb2.add_entry(computer_software, 4_500, Direction.DEBIT)
        tb2.add_entry(cash, 4_500, Direction.CREDIT)
        tx2 = tb2.build()
        tx2.post()

        tb3 = TransactionBuilder(ledger=ledger, description="Test Transaction - 3")
        tb3.set_trans_date("2012-08-3")
        tb3.add_entry(computer_software, 1_250, Direction.DEBIT)
        tb3.add_entry(accts_payable, 1_250, Direction.CREDIT)
        tx3 = tb3.build()
        tx3.post()
        self.assertEqual(LedgerHelper.get_account_balance(cash), 5_500)

        tb4 = TransactionBuilder(ledger=ledger, description="Test Transaction - 4")
        tb4.set_trans_date("2012-08-17")
        tb4.add_entry(accts_payable, 1_250.00, Direction.DEBIT)
        tb4.add_entry(cash, 1_250.00, Direction.CREDIT)
        tx4 = tb4.build()
        tx4.post()
        self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)

        lh = LedgerHelper(ledger)
        # self.logger.info(lh.get_account_summary())

        ac1 = AccountContext(computer_software)
        logger.info(ac1.get_account_console_summary())
