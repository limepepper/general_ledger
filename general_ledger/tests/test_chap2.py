import logging

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


# Create your tests here.
class TestBasicOperations(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_simple_builder_unbalanced(self):
        """
        Test the simple builder with entries that don't balance
        :return:
        """
        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()

        tb = TransactionBuilder()
        tb.set_ledger(ledger)
        tb.set_description("Test Transaction - 1")
        tb.add_entry(
            Account.objects.get(code="102", coa=coa),
            100,
            Direction.CREDIT,
        )
        tb.add_entry(
            Account.objects.get(code="103", coa=coa),
            1000,
            Direction.DEBIT,
        )
        tx = tb.build()

        self.assertIsInstance(tx, Transaction)
        self.assertEqual(tx.description, "Test Transaction - 1")
        self.assertEqual(len(tx.entry_set.all()), 2)
        self.assertFalse(tx.is_valid())

    def test_something_else1(self):

        ledger = Ledger.objects.get(name="ledger-generic-1")

        print(ledger)

        lh = LedgerHelper(ledger)
        tx = lh.build_transaction(
            description="Test Transaction",
            entries=[
                {
                    "account": "102",
                    "amount": 100,
                    "tx_type": constants.TxType.CREDIT,
                },
                {
                    "account": "103",
                    "amount": 100,
                    "tx_type": constants.TxType.DEBIT,
                },
            ],
        )
        print(tx)
        self.assertIsInstance(tx, Transaction)
        self.assertEqual(tx.description, "Test Transaction")

    def test_worked_example_1(self):
        """
        1. Owner starts the business with $10,000 cash on 1 Aug 2019
        2. A van is bought for £4,500 cash on 2 August 2019.
        3. Fixtures (e.g. shelves) are bought on time from Shop Fitters for £1,250 on 3 August 2019.
        4. Paid the amount owing to Shop Fitters in cash on 17 August 2019.
        """

        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()
        cash = Account.objects.get(name="Cash", coa=coa)
        capital = Account.objects.get(name="Capital", coa=coa)
        van, created = coa.account_set.get_or_create(
            coa=coa,
            name="Van",
            defaults={
                "type": book.accounttype_set.get(
                    name="Non-current Asset",
                ),
                "tax_rate": book.taxrate_set.get(
                    name="No VAT",
                ),
            },
        )
        shop_fitters, created = coa.account_set.get_or_create(
            name="Shop Fitters",
            defaults={
                "type": book.accounttype_set.get(
                    name="Current Liability",
                ),
                "tax_rate": book.taxrate_set.get(
                    name="No VAT",
                ),
            },
        )
        fixtures, created = coa.account_set.get_or_create(
            name="Fixtures",
            defaults={
                "type": book.accounttype_set.get(
                    name="Non-current Asset",
                ),
                "tax_rate": book.taxrate_set.get(
                    name="No VAT",
                ),
            },
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
        tb2.add_entry(van, 4_500, Direction.DEBIT)
        tb2.add_entry(cash, 4_500, Direction.CREDIT)
        tx2 = tb2.build()
        tx2.post()

        tb3 = TransactionBuilder(ledger=ledger, description="Test Transaction - 3")
        tb3.set_trans_date("2012-08-3")
        tb3.add_entry(fixtures, 1_250, Direction.DEBIT)
        tb3.add_entry(shop_fitters, 1_250, Direction.CREDIT)
        tx3 = tb3.build()
        tx3.post()
        self.assertEqual(LedgerHelper.get_account_balance(cash), 5_500)

        tb4 = TransactionBuilder(ledger=ledger, description="Test Transaction - 4")
        tb4.set_trans_date("2012-08-17")
        tb4.add_entry(shop_fitters, 1_250, Direction.DEBIT)
        tb4.add_entry(cash, 1_250, Direction.CREDIT)
        tx4 = tb4.build()
        tx4.post()
        self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)

        self.assertIsInstance(tx1, Transaction)
        self.assertIsInstance(tx2, Transaction)
        self.assertIsInstance(tx3, Transaction)
        self.assertIsInstance(tx4, Transaction)

        self.assertEqual(tx1.description, "Test Transaction - 1")
        self.assertEqual(len(tx1.entry_set.all()), 2)
        # self.assertFalse(tx.is_valid())
        self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)
        self.assertTrue(tx1.is_balance_valid())
        self.assertFalse(tx1.can_post())
        # self.assertTrue(False)
        lh = LedgerHelper(ledger)
        self.logger.info(lh.get_account_summary())

        ac = AccountContext(cash)
        self.logger.info(ac.get_context_report())
