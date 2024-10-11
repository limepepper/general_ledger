import pandas as pd
from rich.console import Console

from general_ledger.builders.transaction import TransactionBuilder
from general_ledger.factories import BookFactory
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.django.models.account import Account
from general_ledger.django.models.direction import Direction
from general_ledger.utils.utility import slugu
from general_ledger.utils.data_loader import tx

# from rich import print

console = Console()


def load_chapter_5_data():
    """
    accounts for debtors
    """
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    bank, cash, purchases, purchases_returns, sales, k_tandy, c_lee, k_wood, \
    d_knight, b_walters, e_williams, k_patterson = [
        coa.get_or_create(*args)
        for k, (args) in {
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "purchases": ["Purchases", "direct-costs"],
            "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
            "sales": ["Sales", "sales", "20-vat-on-income"],
            "k_tandy": ["K Tandy", "accounts-receivable", "no-vat"],
            "c_lee": ["C Lee", "accounts-receivable", "no-vat"],
            "k_wood": ["K Wood", "accounts-receivable", "no-vat"],
            "d_knight": ["D Knight", "accounts-receivable", "no-vat"],
            "b_walters": ["B Walters", "accounts-receivable", "no-vat"],
            "e_williams": ["E Williams", "accounts-payable", "no-vat"],
            "k_patterson": ["K Patterson", "accounts-payable", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (k_tandy,      "144", "2012-08-01", sales),
        (d_knight,     "158", "2012-08-01", sales),
        (purchases,    "248", "2012-08-02", e_williams),
        (k_wood,       "214", "2012-08-06", sales),
        (purchases,    "620", "2012-08-08", k_patterson),
        (c_lee,        "177", "2012-08-11", sales),
        (k_patterson,   "20", "2012-08-14", purchases_returns),
        (d_knight,     "206", "2012-08-15", sales),
        (purchases,    "200", "2012-08-15", k_patterson),
        (b_walters,     "51", "2012-08-18", sales),
        (purchases,    "116", "2012-08-18", e_williams),
        (k_tandy,      "300", "2012-08-19", sales),
        (c_lee,        "203", "2012-08-19", sales),
        (e_williams,   "100", "2012-08-21", bank),
        (bank,         "144", "2012-08-22", k_tandy),
        (c_lee,        "100", "2012-08-22", sales),
        (bank,         "158", "2012-08-28", d_knight),
        (bank,         "300", "2012-08-28", k_tandy),
        (k_patterson,  "600", "2012-08-28", bank),
        (bank,         "480", "2012-08-30", c_lee),
        (bank,         "214", "2012-08-30", k_wood),
        (d_knight,     "118", "2012-08-30", sales),
    ]]
    # fmt: on
    return ledger


def load_5_review_5_1_data():
    """
    accounts and transaction for review question 5.1
    """
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()
    # fmt: off
    bank, cash, purchases, purchases_returns, sales, sales_returns, b_flynn, f_start, \
    f_lane, t_fey = [
       coa.get_or_create(*args)
       for k, (args) in {
           "bank": ["Bank Account", "bank"],
           "cash": ["Cash", "cash", "no-vat"],
           "purchases": ["Purchases", "direct-costs"],
           "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
           "sales": ["Sales", "sales"],
           "sales_returns": ["Sales Returns", "current-asset", "no-vat"],
           "b_flynn": ["B Flynn", "accounts-receivable", "no-vat"],
           "f_start": ["F Start", "accounts-receivable", "no-vat"],
           "f_lane": ["F Lane", "accounts-receivable", "no-vat"],
           "t_fey": ["T Fey", "accounts-receivable", "no-vat"],
       }.items()
    ]
    # fmt: on

    transactions_sales = [
        (
            b_flynn,
            "810.00",
            "2019-5-1",
        ),
        (
            f_lane,
            "1100.00",
            "2019-5-1",
        ),
        (
            t_fey,
            "413.00",
            "2019-5-1",
        ),
        (
            f_start,
            "480.00",
            "2019-5-4",
        ),
        (
            b_flynn,
            "134.00",
            "2019-5-4",
        ),
        (
            f_start,
            "240.00",
            "2019-5-31",
        ),
    ]

    transactions_returns_inward = [
        (
            b_flynn,
            "124.00",
            "2019-5-10",
        ),
        (
            t_fey,
            "62.00",
            "2019-5-10",
        ),
    ]

    transactions_payments_received = [
        (
            f_lane,
            "1100.00",
            "2019-5-18",
            bank,
        ),
        (
            t_fey,
            "351.00",
            "2019-5-20",
            bank,
        ),
        (
            b_flynn,
            "440.00",
            "2019-5-24",
            cash,
        ),
    ]

    for entry in transactions_sales:
        LedgerHelper.post_transaction(
            ledger,
            f"Sales on-time to {entry[0].name}",
            entry[2],
            [
                (entry[0], entry[1], Direction.DEBIT),
                (sales, entry[1], Direction.CREDIT),
            ],
        )

    for entry in transactions_returns_inward:
        LedgerHelper.post_transaction(
            ledger,
            f"Returns inward from {entry[0].name}",
            entry[2],
            [
                (entry[0], entry[1], Direction.CREDIT),
                (sales_returns, entry[1], Direction.DEBIT),
            ],
        )

    for entry in transactions_payments_received:
        LedgerHelper.post_transaction(
            ledger,
            f"Payments received from {entry[0].name}",
            entry[2],
            [
                (entry[0], entry[1], Direction.CREDIT),
                (entry[3], entry[1], Direction.DEBIT),
            ],
        )

    return ledger


def load_5_review_5_2_data():
    """
    accounts and transaction for review question 5.2
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
    purchases_returns = coa.get_or_create(
        "Purchases Returns", "current-liability", "no-vat"
    )
    sales = coa.get_or_create("Sales", "sales")
    sales_returns = coa.get_or_create("Sales Returns", "current-asset", "no-vat")
    j_wilson, _ = coa.account_set.get_or_create(
        name="J Wilson",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    p_todd, _ = coa.account_set.get_or_create(
        name="P Todd",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    j_fry, _ = coa.account_set.get_or_create(
        name="J Fry",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )
    p_rake, _ = coa.account_set.get_or_create(
        name="P Rake",
        type=book.accounttype_set.get(slug="accounts-payable"),
        tax_rate=book.taxrate_set.get(slug="no-vat"),
    )

    transactions = [
        (purchases, "240.00", "2019-6-1", j_wilson),
        (purchases, "390.00", "2019-6-1", p_todd),
        (purchases, "1620.00", "2019-6-1", j_fry),
        (purchases, "470.00", "2019-6-3", p_todd),
        (purchases, "290.00", "2019-6-3", p_rake),
        (purchases, "210.00", "2019-6-15", j_wilson),
        (j_fry, "140.00", "2019-6-10", purchases_returns),
        (j_wilson, "65.00", "2019-6-10", purchases_returns),
        (p_todd, "39.00", "2019-6-30", purchases_returns),
        (p_rake, "290.00", "2019-6-19", cash),
        (j_wilson, "300.00", "2019-6-28", cash),
    ]

    for entry in transactions:
        LedgerHelper.post_transaction(
            ledger,
            f"review transactions {entry[0].name}",
            entry[2],
            [
                (entry[0], entry[1], Direction.DEBIT),
                (entry[3], entry[1], Direction.CREDIT),
            ],
        )

    return ledger


def load_5_review_5_5_data():
    """
    accounts and transaction for review question 5.2
    """
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()
    df = pd.read_csv("general_ledger/tests/book/chap_5_review_5_5_data.csv")
    # inspect(df)
    accts = {}
    for index, row in df.iterrows():
        # print(row["name"], row["type_slug"], row["tax_rate_slug"])
        # print(Account.objects.filter(name=row["name"], coa=coa))
        accts[slugu(row["name"])] = coa.get_or_create(
            row["name"], row["type_slug"], row["tax_rate_slug"]
        )

    # inspect(accts)

    transactions = [
        (
            accts["j_bee"],
            "1040.00",
            "2019-9-1",
            accts["sales"],
        ),
        (accts["t_day"], "1260.00", "2019-9-1", accts["sales"]),
        (accts["j_soul"], "480", "2019-9-1", accts["sales"]),
        (accts["purchases"], "780", "2019-9-2", accts["d_blue"]),
        (accts["purchases"], "1020", "2019-9-2", accts["f_rise"]),
        (accts["purchases"], "560", "2019-9-2", accts["p_lee"]),
        (accts["t_day"], "340", "2019-9-8", accts["sales"]),
        (accts["l_hope"], "480", "2019-9-8", accts["sales"]),
        (accts["purchases"], "92", "2019-9-10", accts["f_rise"]),
        (accts["purchases"], "870", "2019-9-10", accts["r_james"]),
        (accts["sales_returns"], "25", "2019-9-12", accts["j_soul"]),
        (accts["sales_returns"], "190", "2019-9-12", accts["t_day"]),
        (accts["purchases_returns"], "12", "2019-9-17", accts["f_rise"]),
        (accts["purchases_returns"], "84", "2019-9-17", accts["r_james"]),
        (accts["d_blue"], "780", "2019-9-20", accts["bank"]),
        (accts["bank"], "900", "2019-9-24", accts["j_bee"]),
        (accts["r_james"], "766", "2019-9-26", accts["bank"]),
        (accts["bank"], "80", "2019-9-28", accts["j_bee"]),
        (accts["bank"], "480", "2019-9-30", accts["l_hope"]),
    ]

    for entry in transactions:
        LedgerHelper.post_transaction(
            ledger,
            f"review transactions {entry[0].name}",
            entry[2],
            [
                (entry[0], entry[1], Direction.DEBIT),
                (entry[3], entry[1], Direction.CREDIT),
            ],
        )

    return ledger
