import logging

from general_ledger.builders import TransactionBuilder
from general_ledger.factories import BookFactory
from general_ledger.helpers import LedgerHelper
from general_ledger.models import (
    Account,
    Direction,
)
from general_ledger.tests import GeneralLedgerBaseTest


# Create your tests here.
class TestChap4Woods(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_4_6(self):
        """
        double entry for expenses and revenue
        """
        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()
        cash = Account.objects.get(name="Cash", coa=coa)
        bank = Account.objects.get(name="Bank Account", coa=coa)
        # capital = Account.objects.get(name="Capital", ledger=ledger)
        purchases, _ = coa.account_set.get_or_create(
            name="Purchases",
            type__slug="direct-costs",
        )
        postage_stamps, _ = coa.account_set.get_or_create(
            name="Postage Stamps",
            type=book.accounttype_set.get(slug="overhead"),
            tax_rate=book.taxrate_set.get_or_create(
                name="Exempt Expenses",
                rate=0,
                tax_type=book.taxtype_set.get(slug="exempt-purchases"),
            )[0],
        )
        electricity, _ = coa.account_set.get_or_create(
            name="Electricity",
            type=book.accounttype_set.get(slug="overhead"),
            tax_rate=book.taxrate_set.get_or_create(
                slug="5-vat-on-expenses",
                tax_type=book.taxtype_set.get(slug="purchases"),
            )[0],
        )
        rent_income, _ = coa.account_set.get_or_create(
            name="Rental Income",
            type=book.accounttype_set.get(slug="other-income"),
            tax_rate=book.taxrate_set.get_or_create(
                slug="exempt-income",
                rate=0,
                name="Exempt Income",
                tax_type=book.taxtype_set.get(slug="exempt-sales"),
            )[0],
        )
        insurance, _ = coa.account_set.get_or_create(
            name="Insurance",
            type=book.accounttype_set.get(slug="overhead"),
            tax_rate=book.taxrate_set.get_or_create(
                name="Exempt Expense",
                slug="exempt-expense",
                rate=0,
                tax_type=book.taxtype_set.get(slug="exempt-purchases"),
            )[0],
        )

        self.logger.debug(purchases)

        tb1 = TransactionBuilder(ledger=ledger, description="Pay postage with cash")
        tb1.set_trans_date("2024-06-1")
        tb1.add_entry(postage_stamps, 50, Direction.DEBIT)
        tb1.add_entry(cash, 50, Direction.CREDIT)
        tx1 = tb1.build()
        self.assertTrue(tx1.can_post())
        tx1.post()

        tb2 = TransactionBuilder(ledger=ledger, description="pay electricity by cheque")
        tb2.set_trans_date("2024-06-2")
        tb2.add_entry(electricity, 229, Direction.DEBIT)
        tb2.add_entry(bank, 229, Direction.CREDIT)
        tx2 = tb2.build()
        tx2.post()
        #
        tb3 = TransactionBuilder(ledger=ledger, description="receive rent in cash")
        tb3.set_trans_date("2024-06-3")
        tb3.add_entry(cash, 138, Direction.DEBIT)
        tb3.add_entry(rent_income, 138, Direction.CREDIT)
        tx3 = tb3.build()
        tx3.post()
        # self.assertEqual(LedgerHelper.get_account_balance(cash), 5_500)
        #
        tb4 = TransactionBuilder(ledger=ledger, description="paid insurance by cheque")
        tb4.set_trans_date("2024-06-4")
        tb4.add_entry(insurance, 142, Direction.DEBIT)
        tb4.add_entry(bank, 142, Direction.CREDIT)
        tx4 = tb4.build()
        tx4.post()
        # self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)
        #
        # # self.logger.info(f"calling save in transaction: {ledger}")
        lh = LedgerHelper(ledger)
        self.logger.debug("\n" + lh.get_account_summary())

    def test_4_7(self):
        """
        double entry for drawings
        """
        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()
        cash = Account.objects.get(name="Cash", coa=coa)
        capital = Account.objects.get(name="Capital", coa=coa)

        drawings, _ = coa.account_set.get_or_create(
            name="Drawings",
            type=book.accounttype_set.get(slug="equity"),
            tax_rate=book.taxrate_set.get_or_create(
                slug="no-vat",
                tax_type=book.taxtype_set.get(slug="no-vat"),
            )[0],
        )

        tb1 = TransactionBuilder(ledger=ledger, description="Owner draws cash")
        tb1.set_trans_date("2024-06-25")
        tb1.add_entry(drawings, 50, Direction.DEBIT)
        tb1.add_entry(cash, 50, Direction.CREDIT)
        tx1 = tb1.build()
        self.assertTrue(tx1.can_post())
        tx1.post()

        #
        # self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)
        #
        # # self.logger.info(f"calling save in transaction: {ledger}")
        lh = LedgerHelper(ledger)
        self.logger.info(lh.get_account_summary())
