from general_ledger.factories import BookFactory
from general_ledger.tests.book.test_chap3 import load_chapter_3_data
from general_ledger.utils.data_loader import tx


def load_chapter_6_data():

    ledger = load_chapter_3_data()
    return ledger


def load_chapter_6_review_6_1_data():
    book = BookFactory(name="Darron")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    purchases, purchases_returns, sales, sales_returns, capital, bank, cash, drawings, loan, machinery, advertising, m_ball, n_chadwick,j_vaughan, electricity = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "direct-costs"],
            "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
            "sales": ["Sales", "sales", "20-vat-on-income"],
            "sales_returns": ["Sales Returns", "current-asset", "20-vat-on-income"],
            "capital": ["Capital", "equity", "no-vat"],
            "bank_account": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "loan_account": ["Loan Account", "non-current-liability"],
            "machinery": ["Machinery", "non-current-asset", "no-vat"],
            "advertising": ["Advertising", "expense", "20-vat-on-expenses"],
            "m_ball": ["M Ball", "accounts-payable", "no-vat"],
            "n_chadwick": ["N Chadwick", "accounts-receivable", "no-vat"],
            "j_vaughan": ["j Vaughan", "accounts-receivable", "no-vat"],
            "electricity": ["Electricity", "expense", "20-vat-on-expenses"],
        }.items()
    ]
    # fmt: on


    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr, amt, dt, cr) for dr, amt, dt, cr in [
        (bank,         "800", "2020-05-1",  capital),
        (bank,        "2000", "2020-5-3",   loan),
        (machinery,   "2500", "2020-5-5",   bank),
        (advertising,   "75", "2020-5-7",   bank),
        (purchases,    "200", "2020-5-9",   bank),
        (purchases,    "700", "2020-5-11",  m_ball),
        (bank,         "380", "2020-5-13",  sales),
        (n_chadwick,   "470", "2020-5-15",  sales),
        (j_vaughan,    "550", "2020-5-17",  sales),
        (drawings,     "110", "2020-5-19",  bank),
        (sales_returns, "60", "2020-5-21",  j_vaughan),
        (m_ball,       "300", "2020-5-23",  bank),
        (bank,         "170", "2020-5-25",  n_chadwick),
        (electricity,  "145", "2020-5-31",  bank),
    ]]
    # fmt: on

    return ledger


def load_chapter_6_review_6_2_data():
    book = BookFactory(name="Nicola Burt")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    purchases, purchases_returns, sales, capital, bank, cash, drawings, loan, machinery, computer_equipment, d_bellini, j_adams, tvc_ltd, g_plover, wages = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "direct-costs"],
            "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
            "sales": ["Sales", "sales"],
            "capital": ["Capital", "equity", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "loan": ["Loan Account", "non-current-liability"],
            "machinery": ["Machinery", "non-current-asset", "no-vat"],
            "computer_equipment": ["Computer Equipment", "non-current-asset", "no-vat"],
            "d_bellini": ["D Bellini", "accounts-payable", "no-vat"],
            "j_adams": ["J Adams", "accounts-receivable", "no-vat"],
            "tvc_ltd": ["TVC Ltd", "accounts-payable", "no-vat"],
            "g_plover": ["G Plover", "non-current-liability", "no-vat"],
            "wages": ["Wages", "expense", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (cash,               "3850", "2023-08-01", capital),
        (bank,               "3500", "2023-08-02", cash),
        (purchases,          "414",  "2023-08-04", d_bellini),
        (machinery,          "2500", "2023-08-05", bank),
        (purchases,          "323",  "2023-08-07", cash),
        (j_adams,            "595",  "2023-08-10", sales),
        (drawings,           "98",   "2023-08-11", purchases),
        (d_bellini,          "70",   "2023-08-12", purchases_returns),
        (cash,               "328",  "2023-08-19", sales),
        (computer_equipment, "1450", "2023-08-22", tvc_ltd),
        (bank,               "2000", "2023-08-24", loan),
        (d_bellini,          "180",  "2023-08-29", bank),
        (wages,              "530",  "2023-08-30", bank),
        (tvc_ltd,            "1450", "2023-08-31", bank),
    ]]
    # fmt: on

    return ledger


def load_chapter_6_review_6_5_data():

    book = BookFactory(name="M Donnelly")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    (
        purchases, purchases_returns, sales, sales_returns, capital, bank, cash, drawings, machinery, insurance, p_thomas, m_wilkinson, e_grant, e_williams, m_donnelly, wages,
    ) = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "direct-costs"],
            "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
            "sales": ["Sales", "sales"],
            "sales_returns": ["Sales Returns", "current-asset", "20-vat-on-income"],
            "capital": ["Capital", "equity", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "machinery": ["Machinery", "non-current-asset", "no-vat"],
            "insurance": ["Insurance", "overhead", "no-vat"],
            "p_thomas": ["P Thomas", "accounts-payable", "no-vat"],
            "m_wilkinson": ["M Wilkinson", "accounts-payable", "no-vat"],
            "e_grant": ["E Grant", "accounts-receivable", "no-vat"],
            "e_williams": ["E Williams", "accounts-receivable", "no-vat"],
            "m_donnelly": ["M Donnelly", "accounts-payable", "no-vat"],
            "wages": ["Wages", "expense", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [
        tx(ledger, dr, amt, dt, cr)
        for dr, amt, dt, cr in [
            (cash,         "500", "2023-04-01", capital),
            (bank,        "3000", "2023-04-01", capital),
            (purchases,    "475", "2023-04-05", p_thomas),
            (machinery,   "1450", "2023-04-06", bank),
            (insurance,    "120", "2023-04-07", bank),
            (purchases,    "255", "2023-04-09", m_wilkinson),
            (e_grant,      "700", "2023-04-12", sales),
            (cash,         "300", "2023-04-15", sales),
            (p_thomas,     "475", "2023-04-20", bank),
            (m_wilkinson,   "50", "2023-04-22", purchases_returns),
            (e_williams,   "325", "2023-04-24", sales),
            (wages,         "45", "2023-04-25", bank),
            (sales_returns, "80", "2023-04-27", e_grant),
            (drawings,      "80", "2023-04-30", cash),
        ]
    ]
    # fmt: on

    return ledger
