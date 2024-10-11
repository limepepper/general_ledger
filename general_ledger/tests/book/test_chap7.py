from general_ledger.builders import TransactionBuilder
from general_ledger.factories import BookFactory
from general_ledger.models import Direction

def load_exhibit_7_1():
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    general_expenses, _ = coa.account_set.get_or_create(
        name="General Expenses",
        type=book.accounttype_set.get(slug="overhead"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-expenses"),
    )
    sales, _ = coa.account_set.get_or_create(
        name="Sales",
        type=book.accounttype_set.get(slug="sales"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-income"),
    )
    drawings, _ = coa.account_set.get_or_create(
        name="Drawings",
        type=book.accounttype_set.get(slug="equity"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    fixtures, _ = coa.account_set.get_or_create(
        name="Fixtures",
        type=book.accounttype_set.get(slug="non-current-asset"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-expenses"),
    )
    purchases = coa.account_set.get(
        name="Purchases",
        type__slug="direct-costs",
    )
    accounts_receivable = coa.account_set.get(
        name="Accounts Receivable",
        type__slug="accounts-receivable",
    )
    accounts_payable = coa.account_set.get(
        name="Accounts Payable",
        type__slug="accounts-payable",
    )
    inventory = coa.account_set.get(
        name="Inventory",
        type__slug="current-asset",
    )
    bank = coa.account_set.get(name="Bank Account", coa=coa)
    cash = coa.account_set.get(name="Cash", coa=coa)
    capital = coa.account_set.get(name="Capital", coa=coa)
    opening_balances = coa.account_set.get(name="Opening Balances", coa=coa)

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "38500.00", Direction.DEBIT)
    tb.add_entry(sales, "38500.00", Direction.CREDIT)
    tb.build().post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "600.00", Direction.CREDIT)
    tb.add_entry(general_expenses, "600.00", Direction.DEBIT)
    tb.build().post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "7000.00", Direction.CREDIT)
    tb.add_entry(drawings, "7000.00", Direction.DEBIT)
    tb.build().post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "5000.00", Direction.CREDIT)
    tb.add_entry(fixtures, "5000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "6800.00", Direction.CREDIT)
    tb.add_entry(accounts_receivable, "6800.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(accounts_payable, "9100.00", Direction.CREDIT)
    tb.add_entry(opening_balances, "9100.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "3000.00", Direction.CREDIT)
    tb.add_entry(inventory, "3000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "15100.00", Direction.CREDIT)
    tb.add_entry(bank, "15100.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "200.00", Direction.CREDIT)
    tb.add_entry(cash, "200.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(capital, "20000.00", Direction.CREDIT)
    tb.add_entry(opening_balances, "20000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    return ledger


def load_exhibit_7_3():
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    fixtures, _ = coa.account_set.get_or_create(
        name="Fixtures",
        type=book.accounttype_set.get(slug="non-current-asset"),
        tax_rate=book.taxrate_set.get(slug="20-vat-on-expenses"),
    )
    purchases = coa.account_set.get(
        name="Purchases",
        type__slug="direct-costs",
    )
    accounts_receivable = coa.account_set.get(
        name="Accounts Receivable",
        type__slug="accounts-receivable",
    )
    accounts_payable = coa.account_set.get(
        name="Accounts Payable",
        type__slug="accounts-payable",
    )
    inventory = coa.account_set.get(
        name="Inventory",
        type__slug="current-asset",
    )
    bank = coa.account_set.get(name="Bank Account", coa=coa)
    cash = coa.account_set.get(name="Cash", coa=coa)
    capital = coa.account_set.get(name="Capital", coa=coa)
    opening_balances = coa.account_set.get(name="Opening Balances", coa=coa)

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "5000.00", Direction.CREDIT)
    tb.add_entry(fixtures, "5000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "6800.00", Direction.CREDIT)
    tb.add_entry(accounts_receivable, "6800.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(accounts_payable, "9100.00", Direction.CREDIT)
    tb.add_entry(opening_balances, "9100.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "3000.00", Direction.CREDIT)
    tb.add_entry(inventory, "3000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "15100.00", Direction.CREDIT)
    tb.add_entry(bank, "15100.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(opening_balances, "200.00", Direction.CREDIT)
    tb.add_entry(cash, "200.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    tb = TransactionBuilder(
        ledger=ledger,
        description="Opening Balance",
    )
    tb.set_trans_date("2012-12-1")
    tb.add_entry(capital, "21000.00", Direction.CREDIT)
    tb.add_entry(opening_balances, "21000.00", Direction.DEBIT)
    tx = tb.build()
    assert tx.can_post()
    tx.post()

    return ledger
