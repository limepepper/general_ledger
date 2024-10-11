from general_ledger.builders import TransactionBuilder
from general_ledger.factories import BookFactory
from general_ledger.models import Direction


def get_or_create_account(coa, name, slug=None, tax_slug=None):
    account_type = coa.book.accounttype_set.get(slug=slug) if slug else None
    tax_rate = coa.book.taxrate_set.get(slug=tax_slug) if tax_slug else None
    account, _ = coa.account_set.get_or_create(
        name=name,
        type=account_type,
        tax_rate=tax_rate,
    )
    return account


def post_transaction(ledger, description, date, entries):
    tb = TransactionBuilder(ledger=ledger, description=description)
    tb.set_trans_date(date)
    for account, amount, direction in entries:
        tb.add_entry(account, amount, direction)
    tb.build().post()


def load_exhibit_7_1():
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    general_expenses = get_or_create_account(
        coa, "General Expenses", "overhead", "20-vat-on-expenses"
    )
    drawings = get_or_create_account(coa, "Drawings", "equity", "no-vat")
    fixtures = get_or_create_account(
        coa, "Fixtures", "non-current-asset", "20-vat-on-expenses"
    )
    rent = get_or_create_account(coa, "Rent", "overhead", "20-vat-on-expenses")
    lighting = get_or_create_account(
        coa, "Lighting Expenses", "overhead", "5-vat-on-expenses"
    )
    sales = coa.account_set.get(name="Sales")
    purchases = coa.account_set.get(name="Purchases")
    accounts_receivable = coa.account_set.get(name="Accounts Receivable")
    accounts_payable = coa.account_set.get(name="Accounts Payable")
    inventory = coa.account_set.get(name="Inventory")
    bank = coa.account_set.get(name="Bank Account")
    cash = coa.account_set.get(name="Cash")
    capital = coa.account_set.get(name="Capital")
    opening_balances = coa.account_set.get(name="Opening Balances")

    transactions = [
        (
            opening_balances,
            "38500.00",
            Direction.DEBIT,
            sales,
            "38500.00",
            Direction.CREDIT,
        ),
        (
            opening_balances,
            "600.00",
            Direction.CREDIT,
            general_expenses,
            "600.00",
            Direction.DEBIT,
        ),
        (
            opening_balances,
            "7000.00",
            Direction.CREDIT,
            drawings,
            "7000.00",
            Direction.DEBIT,
        ),
        (
            opening_balances,
            "5000.00",
            Direction.CREDIT,
            fixtures,
            "5000.00",
            Direction.DEBIT,
        ),
        (
            opening_balances,
            "6800.00",
            Direction.CREDIT,
            accounts_receivable,
            "6800.00",
            Direction.DEBIT,
        ),
        (
            accounts_payable,
            "9100.00",
            Direction.CREDIT,
            opening_balances,
            "9100.00",
            Direction.DEBIT,
        ),
        (
            opening_balances,
            "3000.00",
            Direction.CREDIT,
            inventory,
            "3000.00",
            Direction.DEBIT,
        ),
        (
            opening_balances,
            "15100.00",
            Direction.CREDIT,
            bank,
            "15100.00",
            Direction.DEBIT,
        ),
        (opening_balances, "200.00", Direction.CREDIT, cash, "200.00", Direction.DEBIT),
        (
            capital,
            "20000.00",
            Direction.CREDIT,
            opening_balances,
            "20000.00",
            Direction.DEBIT,
        ),
        (
            purchases,
            "29000.00",
            Direction.DEBIT,
            opening_balances,
            "29000.00",
            Direction.CREDIT,
        ),
        (
            lighting,
            "1500.00",
            Direction.DEBIT,
            opening_balances,
            "1500.00",
            Direction.CREDIT,
        ),
        (
            rent,
            "2400.00",
            Direction.DEBIT,
            opening_balances,
            "2400.00",
            Direction.CREDIT,
        ),
    ]

    for entry in transactions:
        post_transaction(
            ledger,
            "Opening Balance",
            "2012-12-1",
            [(entry[0], entry[1], entry[2]), (entry[3], entry[4], entry[5])],
        )

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
        type__slug="inventory",
    )
    bank = coa.account_set.get(name="Bank Account")
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
