import logging
from decimal import Decimal

from django.db import connection
from django.shortcuts import render
from django.template.loader import get_template

from general_ledger.builders import TransactionBuilder
from general_ledger.factories import BookFactory
from general_ledger.helpers import LedgerHelper
from general_ledger.models import (
    Account,
    Ledger,
    Direction,
)
from general_ledger.tests import GeneralLedgerBaseTest


def load_chapter_5_data():
    """
    accounts for debtors
    """
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()
    bank = Account.objects.get(name="Bank Account", coa=coa)
    cash = Account.objects.get(name="Cash", coa=coa)
    purchases, _ = coa.account_set.get_or_create(
        name="Purchases",
        type__slug="direct-costs",
    )
    purchases_returns, _ = coa.account_set.get_or_create(
        name="Purchases Returns",
        type=book.accounttype_set.get(slug="current-liability"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    sales, _ = coa.account_set.get_or_create(
        name="Sales",
        type=book.accounttype_set.get(slug="sales"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-income"),
    )
    k_tandy, _ = coa.account_set.get_or_create(
        name="K Tandy",
        type=book.accounttype_set.get(slug="accounts-receivable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    c_lee, _ = coa.account_set.get_or_create(
        name="C Lee",
        type=book.accounttype_set.get(slug="accounts-receivable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    k_wood, _ = coa.account_set.get_or_create(
        name="K Wood",
        type=book.accounttype_set.get(slug="accounts-receivable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    d_knight, _ = coa.account_set.get_or_create(
        name="D Knight",
        type=book.accounttype_set.get(slug="accounts-receivable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    b_walters, _ = coa.account_set.get_or_create(
        name="B Walters",
        type=book.accounttype_set.get(slug="accounts-receivable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    e_williams, _ = coa.account_set.get_or_create(
        name="E Williams",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    k_patterson, _ = coa.account_set.get_or_create(
        name="K Patterson",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    tb = TransactionBuilder(ledger=ledger, description="sales to K tandy")
    tb.set_trans_date("2012-08-1")
    tb.add_entry(sales, 144, Direction.CREDIT)
    tb.add_entry(k_tandy, 144, Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to K tandy")
    tb.set_trans_date("2012-08-19")
    tb.add_entry(sales, 300, Direction.CREDIT)
    tb.add_entry(k_tandy, 300, Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="payment by K tandy")
    tb.set_trans_date("2012-08-22")
    tb.add_entry(bank, 144, Direction.DEBIT)
    tb.add_entry(k_tandy, 144, Direction.CREDIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="payment by K tandy")
    tb.set_trans_date("2012-08-28")
    tb.add_entry(bank, 300, Direction.DEBIT)
    tb.add_entry(k_tandy, 300, Direction.CREDIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to C Lee on credit")
    tb.set_trans_date("2012-08-11")
    tb.add_entry(sales, 177, Direction.CREDIT)
    tb.add_entry(c_lee, 177, Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to C Lee on credit")
    tb.set_trans_date("2012-08-19")
    tb.add_entry(sales, Decimal(203.00), Direction.CREDIT)
    tb.add_entry(c_lee, Decimal(203.00), Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to C Lee on credit")
    tb.set_trans_date("2012-08-22")
    tb.add_entry(sales, 100, Direction.CREDIT)
    tb.add_entry(c_lee, 100, Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="payment by c lee")
    tb.set_trans_date("2012-08-30")
    tb.add_entry(bank, 480, Direction.DEBIT)
    tb.add_entry(c_lee, 480, Direction.CREDIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to K wood on credit")
    tb.set_trans_date("2012-08-6")
    tb.add_entry(sales, 214, Direction.CREDIT)
    tb.add_entry(k_wood, 214, Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="payment by k wood")
    tb.set_trans_date("2012-08-30")
    tb.add_entry(bank, 214, Direction.DEBIT)
    tb.add_entry(k_wood, 214, Direction.CREDIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="sales to d knight")
    tb.set_trans_date("2012-08-1")
    tb.add_entry(sales, 158, Direction.CREDIT)
    tb.add_entry(d_knight, 158, Direction.DEBIT)
    tx = tb.build()
    tx.post()

    tb2 = TransactionBuilder(ledger=ledger, description="sales to d knight")
    tb2.set_trans_date("2012-08-15")
    tb2.add_entry(sales, 206, Direction.CREDIT)
    tb2.add_entry(d_knight, 206, Direction.DEBIT)
    tx2 = tb2.build()
    tx2.post()

    tb2 = TransactionBuilder(ledger=ledger, description="sales to d knight")
    tb2.set_trans_date("2012-08-30")
    tb2.add_entry(sales, 118, Direction.CREDIT)
    tb2.add_entry(d_knight, 118, Direction.DEBIT)
    tx2 = tb2.build()
    tx2.post()

    tb = TransactionBuilder(
        ledger=ledger, description="receive payment from k knight"
    )
    tb.set_trans_date("2012-08-28")
    tb.add_entry(bank, 158, Direction.DEBIT)
    tb.add_entry(d_knight, 158, Direction.CREDIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger, description="receive payment from k knight"
    )
    tb.set_trans_date("2012-08-18")
    tb.add_entry(sales, 51, Direction.CREDIT)
    tb.add_entry(b_walters, 51, Direction.DEBIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Purchases from E williams")
    tb.set_trans_date("2012-08-2")
    tb.add_entry(purchases, 248, Direction.DEBIT)
    tb.add_entry(e_williams, 248, Direction.CREDIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Purchases from E williams")
    tb.set_trans_date("2012-08-18")
    tb.add_entry(purchases, 116, Direction.DEBIT)
    tb.add_entry(e_williams, 116, Direction.CREDIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb.set_trans_date("2012-08-21")
    tb.add_entry(bank, 100, Direction.CREDIT)
    tb.add_entry(e_williams, 100, Direction.DEBIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb.set_trans_date("2012-08-8")
    tb.add_entry(purchases, 620, Direction.DEBIT)
    tb.add_entry(k_patterson, 620, Direction.CREDIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb.set_trans_date("2012-08-15")
    tb.add_entry(purchases, 200, Direction.DEBIT)
    tb.add_entry(k_patterson, 200, Direction.CREDIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb.set_trans_date("2012-08-28")
    tb.add_entry(bank, 600, Direction.CREDIT)
    tb.add_entry(k_patterson, 600, Direction.DEBIT)
    tx = tb.build()
    tx.post()

    tb = TransactionBuilder(ledger=ledger, description="Test Transaction - 12")
    tb.set_trans_date("2012-08-14")
    tb.add_entry(purchases_returns, 20, Direction.CREDIT)
    tb.add_entry(k_patterson, 20, Direction.DEBIT)
    tx = tb.build()
    tx.post()

    return ledger


# Create your tests here.
class TestChap5Woods(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    

    def test_5_1(self):

        # tb4 = TransactionBuilder(ledger=ledger, description="paid insurance by cheque")
        # tb4.set_trans_date("2024-08-28")
        # tb4.add_entry(d_knight, 158, Direction.CREDIT)
        # tb4.add_entry(bank, 158, Direction.DEBIT)
        # tx4 = tb4.build()
        # tx4.post()

        ledger = load_chapter_5_data()

        # lh = LedgerHelper(ledger)
        # self.logger.info(lh.get_account_summary())

        template = get_template("gl/console/three_col_accounts.j2")

        context = {
            "ledger": ledger,
            "accounts": Account.objects.filter(coa=ledger.coa),
        }

        self.logger.info(template.render(context=context))

        print(template.render(context=context))

        # bank = Account.objects.get(name="Bank Account", coa=self.invoice.ledger.coa)
        # cash = Account.objects.get(name="Cash", coa=self.invoice.ledger.coa)
        # purchases, _ = Account.objects.get_or_create(
        #     coa=self.invoice.ledger.coa,
        #     name="Purchases",
        #     type__name="Direct Costs",
        # )
        # sales, _ = Account.objects.get_or_create(
        #     coa=self.invoice.ledger.coa,
        #     name="Sales",
        #     type__name="Sales",
        # )
        # vat_charged, _ = Account.objects.get_or_create(
        #     coa=self.invoice.ledger.coa,
        #     name="VAT Charged",
        #     type=AccountType.objects.get(
        #         name="Current Liability",
        #         book=self.invoice.ledger.book,
        #     ),
        #     defaults={
        #         "tax_rate": TaxRate.objects.get(
        #             slug="no-vat",
        #             book=self.invoice.ledger.book,
        #         )
        #     },
        # )
        # accounts_receivable, _ = Account.objects.get_or_create(
        #     coa=self.invoice.ledger.coa,
        #     name="Accounts Receivable",
        #     type__name="Current Asset",
        # )
