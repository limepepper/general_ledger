import logging
import pytest
from general_ledger import constants
from general_ledger.factories import BookFactory, LedgerFactory
from general_ledger.helpers import LedgerHelper
from general_ledger.models import (
    Transaction,
    Account,
    Ledger,
    Direction,
    AccountType,
    TaxRate,
    Entry,
)
from general_ledger.tests import GeneralLedgerBaseTest

from general_ledger.builders import TransactionBuilder


def load_chapter_3_data():
    """
    1. Started a household machines business putting £2 ,000 into a
    bank account.
    2. Bought equipment on time from house supplies £12,000.


    """
    book = BookFactory(name="B. Swift")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()
    # cash = Account.objects.get(name="Cash", ledger=ledger)
    # capital = Account.objects.get(name="Capital", ledger=ledger)
    purchases, _ = coa.account_set.get_or_create(
        name="Purchases",
        type__slug="direct-costs",
    )

    sales_returns, _ = coa.account_set.get_or_create(
        name="Sales Returns",
        type=book.accounttype_set.get(slug="current-asset"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-income"),
    )
    sales, _ = coa.account_set.get_or_create(
        name="Sales",
        type=book.accounttype_set.get(slug="sales"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-income"),
    )

    purchases_returns, _ = coa.account_set.get_or_create(
        name="Purchases Returns",
        type=book.accounttype_set.get(slug="current-liability"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    cash = Account.objects.get(name="Cash", coa=coa)
    capital = Account.objects.get(name="Capital", coa=coa)

    d_small, _ = coa.account_set.get_or_create(
        name="D Small",
        type=book.accounttype_set.get(slug="current-liability"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    a_lyon, _ = coa.account_set.get_or_create(
        name="A Lyon & Son",
        type=book.accounttype_set.get(slug="current-liability"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    d_hughes, _ = coa.account_set.get_or_create(
        name="D Hughes",
        type=book.accounttype_set.get(slug="current-asset"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    m_spencer, _ = coa.account_set.get_or_create(
        name="M Spencer",
        type=book.accounttype_set.get(slug="current-asset"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    tb1 = TransactionBuilder(ledger=ledger, description="Test Transaction - 1")
    tb1.set_trans_date("2013-05-1")
    tb1.add_entry(purchases, 220, Direction.DEBIT)
    tb1.add_entry(d_small, 220, Direction.CREDIT)
    tx1 = tb1.build()
    assert tx1.can_post()
    tx1.post()

    tb2 = TransactionBuilder(ledger=ledger, description="Test Transaction - 2")
    tb2.set_trans_date("2013-05-2")
    tb2.add_entry(purchases, 410, Direction.DEBIT)
    tb2.add_entry(a_lyon, 410, Direction.CREDIT)
    tx2 = tb2.build()
    tx2.post()

    tb3 = TransactionBuilder(ledger=ledger, description="Test Transaction - 3")
    tb3.set_trans_date("2013-05-5")
    tb3.add_entry(sales, 60, Direction.CREDIT)
    tb3.add_entry(d_hughes, 60, Direction.DEBIT)
    tx3 = tb3.build()
    tx3.post()
    # self.assertEqual(LedgerHelper.get_account_balance(cash), 5_500)

    tb4 = TransactionBuilder(ledger=ledger, description="Test Transaction - 4")
    tb4.set_trans_date("2013-05-6")
    tb4.add_entry(sales, 45, Direction.CREDIT)
    tb4.add_entry(m_spencer, 45, Direction.DEBIT)
    tx4 = tb4.build()
    tx4.post()
    # self.assertEqual(LedgerHelper.get_account_balance(cash), 4_250)

    tb5 = TransactionBuilder(ledger=ledger, description="Test Transaction - 5")
    tb5.set_trans_date("2013-05-10")
    tb5.add_entry(d_small, 15, Direction.DEBIT)
    tb5.add_entry(purchases_returns, 15, Direction.CREDIT)
    tx5 = tb5.build()
    tx5.post()

    tb6 = TransactionBuilder(ledger=ledger, description="Test Transaction - 6")
    tb6.set_trans_date("2013-05-11")
    tb6.add_entry(cash, 210, Direction.DEBIT)
    tb6.add_entry(sales, 210, Direction.CREDIT)
    tx6 = tb6.build()
    tx6.post()

    tb7 = TransactionBuilder(ledger=ledger, description="Test Transaction - 7")
    tb7.set_trans_date("2013-05-12")
    tb7.add_entry(purchases, 150, Direction.DEBIT)
    tb7.add_entry(cash, 150, Direction.CREDIT)
    tx7 = tb7.build()
    tx7.post()

    tb8 = TransactionBuilder(ledger=ledger, description="Test Transaction - 8")
    tb8.set_trans_date("2013-05-19")
    tb8.add_entry(m_spencer, 16, Direction.CREDIT)
    tb8.add_entry(sales_returns, 16, Direction.DEBIT)
    tx8 = tb8.build()
    tx8.post()

    tb9 = TransactionBuilder(ledger=ledger, description="Test Transaction - 8")
    tb9.set_trans_date("2013-05-21")
    tb9.add_entry(cash, 175, Direction.DEBIT)
    tb9.add_entry(sales, 175, Direction.CREDIT)
    tx9 = tb9.build()
    tx9.post()

    tb10 = TransactionBuilder(ledger=ledger, description="Test Transaction - 10")
    tb10.set_trans_date("2013-05-21")
    tb10.add_entry(cash, 205, Direction.CREDIT)
    tb10.add_entry(d_small, 205, Direction.DEBIT)
    tx10 = tb10.build()
    tx10.post()

    tb11 = TransactionBuilder(ledger=ledger, description="Test Transaction - 11")
    tb11.set_trans_date("2013-05-30")
    tb11.add_entry(cash, 60, Direction.DEBIT)
    tb11.add_entry(d_hughes, 60, Direction.CREDIT)
    tx11 = tb11.build()
    tx11.post()

    tb12 = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb12.set_trans_date("2013-05-31")
    tb12.add_entry(purchases, 214, Direction.DEBIT)
    tb12.add_entry(a_lyon, 214, Direction.CREDIT)
    tx12 = tb12.build()
    tx12.post()

    return ledger


# Create your tests here.
class TestBasicOperations2:

    logger = logging.getLogger(__name__)

    @pytest.mark.django_db
    def test_something_else1(self):

        ledger = LedgerFactory()

    @pytest.mark.django_db
    def test_chapter_3_inventory(self, tmp_path):

        ledger = load_chapter_3_data()

        # self.logger.info(f"calling save in transaction: {ledger}")
        lh = LedgerHelper(ledger)
        print(lh.get_account_summary())

        from django.core import serializers

        d = tmp_path / "sub"
        d.mkdir()
        p = d / "hello.txt"

        data = serializers.serialize("yaml", Transaction.objects.all())
        out = open(d / "transactions1.yaml", "w")
        out.write(data)
        out.close()

        data = serializers.serialize("yaml", Entry.objects.all())
        out = open(d / "entries1.yaml", "w")
        out.write(data)
        out.close()

        data = serializers.serialize("yaml", Account.objects.all())
        out = open(d / "accounts1.yaml", "w")
        out.write(data)
        out.close()
