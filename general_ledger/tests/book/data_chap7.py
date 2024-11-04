from general_ledger.factories import BookFactory
from general_ledger.utils.data_loader import tx


def load_chapter_7_exhibit_7_1():
    book = BookFactory(name="B Swift")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    sales, purchases, rent, lighting, general_expenses, fixtures, trade_receivables, trade_payables, bank, cash, drawings, capital, opening_balances, inventory = [
        coa.get_or_create(*args)
        for k, (args) in {
            "sales": ["Sales", "sales"],
            "purchases": ["Purchases", "purchases", "no-vat"],
            "rent": ["Rent", "overhead", "no-vat"],
            "lighting": ["Lighting Expenses", "overhead", "no-vat"],
            "general_expenses": ["General Expenses", "overhead", "no-vat"],
            "fixtures": ["Fixtures and Fittings", "non-current-asset", "20-vat-on-expenses"],
            "trade_receivables": ["Trade Receivables", "accounts-receivable", "no-vat"],
            "trade_payables": ["Trade Payables", "accounts-payable", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "capital": ["Capital", "equity", "no-vat"],
            "opening_balances": ["Opening Balances", "opening-balances", "no-vat"],
            "inventory": ["Inventory", "inventory", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr, amt, dt, cr) for dr, amt,dt, cr in [
        (opening_balances,   "38500", "2019-01-01", sales),
        (general_expenses,     "600", "2019-01-01", opening_balances),
        (drawings,            "7000", "2019-01-01", opening_balances),
        (fixtures,            "5000", "2019-01-01", opening_balances),
        (trade_receivables,   "6800", "2019-01-01", opening_balances),
        (opening_balances,    "9100", "2019-01-01", trade_payables),
        (bank,               "15100", "2019-01-01", opening_balances),
        (cash,                 "200", "2019-01-01", opening_balances),
        (opening_balances,   "20000", "2019-01-01", capital),
        (lighting,            "1500", "2019-01-01", opening_balances),
        (purchases,          "29000", "2019-01-01", opening_balances),
        (rent,                "2400", "2019-01-01", opening_balances),
        # (inventory,           "3000", "2019-01-01", opening_balances),
    ]]
    # fmt: on

    return ledger


def load_chapter_7_activity_7_4():
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()


def load_chapter_7_exhibit_7_3():
    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    fixtures, trade_receivables, trade_payables, bank, cash, drawings, capital, opening_balances, inventory = [
        coa.get_or_create(*args)
        for k, (args) in {
            "fixtures": ["Fixtures and Fittings", "non-current-asset", "20-vat-on-expenses"],
            "trade_receivables": ["Trade Receivables", "accounts-receivable", "no-vat"],
            "trade_payables": ["Trade Payables", "accounts-payable", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "capital": ["Capital", "equity", "no-vat"],
            "opening_balances": ["Opening Balances", "opening-balances", "no-vat"],
            "inventory": ["Inventory", "inventory", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr, amt, dt, cr) for dr, amt, dt,cr in [
        (fixtures,            "5000", "2019-01-01", opening_balances),
        (trade_receivables,   "6800", "2019-01-01", opening_balances),
        (opening_balances,    "9100", "2019-01-01", trade_payables),
        (bank,               "15100", "2019-01-01", opening_balances),
        (cash,                 "200", "2019-01-01", opening_balances),
        (opening_balances,   "21000", "2019-01-01", capital),
        (inventory,           "3000", "2019-01-01", opening_balances),
    ]]
    # fmt: on

    return ledger


def load_chapter_7_review_7_1():

    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    purchases, sales, salaries, motor_expenses, rent, insurance, general_expenses, premises, \
    motor_vehicles, trade_receivables, trade_payables, bank, cash, drawings, capital, opening_balances, inventory = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "purchases"],
            "sales": ["Sales", "sales"],
            "salaries": ["Salaries", "overhead", "no-vat"],
            "motor_expenses": ["Motor Expenses", "overhead", "no-vat"],
            "rent": ["Rent", "overhead", "no-vat"],
            "insurance": ["Insurance", "overhead", "no-vat"],
            "general_expenses": ["General Expenses", "overhead", "no-vat"],
            "premises": ["Premises", "non-current-asset", "no-vat"],
            "motor_vehicles": ["Motor Vehicles", "non-current-asset", "no-vat"],
            "trade_receivables": ["Trade Receivables", "accounts-receivable", "no-vat"],
            "trade_payables": ["Trade Payables", "accounts-payable", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "cash": ["Cash", "cash", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "capital": ["Capital", "equity", "no-vat"],
            "opening_balances": ["Opening Balances", "opening-balances", "no-vat"],
            "inventory": ["Inventory", "inventory", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (purchases,         "60400", "2023-10-31", opening_balances),
        (salaries,          "29300", "2023-10-31", opening_balances),
        (motor_expenses,     "1200", "2023-10-31", opening_balances),
        (rent,                "950", "2023-10-31", opening_balances),
        (insurance,           "150", "2023-10-31", opening_balances),
        (general_expenses,     "85", "2023-10-31", opening_balances),
        (premises,          "47800", "2023-10-31", opening_balances),
        (motor_vehicles,     "8600", "2023-10-31", opening_balances),
        (trade_receivables, "13400", "2023-10-31", opening_balances),
        (bank,               "8200", "2023-10-31", opening_balances),
        (cash,                "300", "2023-10-31", opening_balances),
        (drawings,           "4200", "2023-10-31", opening_balances),
        (opening_balances, "100250", "2023-10-31", sales),
        (opening_balances,   "8800", "2023-10-31", trade_payables),
        (opening_balances,  "65535", "2023-10-31", capital),
        (inventory,         "15600", "2023-10-31", opening_balances),
    ]]
    # fmt: on

    return ledger


def load_chapter_7_review_7_2():

    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    purchases, sales, rent, lighting_heating, salaries_wages, insurance, buildings, \
        fixtures, trade_receivables, sundry_expenses, trade_payables, bank, drawings, \
        vans, motor_expenses, capital, opening_balances, inventory = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "purchases"],
            "sales": ["Sales", "sales"],
            "rent": ["Rent", "overhead", "no-vat"],
            "lighting_heating": ["Lighting and Heating", "overhead", "no-vat"],
            "salaries_wages": ["Salaries and Wages", "overhead", "no-vat"],
            "insurance": ["Insurance", "overhead", "no-vat"],
            "buildings": ["Buildings", "non-current-asset", "no-vat"],
            "fixtures": ["Fixtures", "non-current-asset", "no-vat"],
            "trade_receivables": ["Trade Receivables", "accounts-receivable", "no-vat"],
            "sundry_expenses": ["Sundry Expenses", "overhead", "no-vat"],
            "trade_payables": ["Trade Payables", "accounts-payable", "no-vat"],
            "bank": ["Bank Account", "bank"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "vans": ["Vans", "non-current-asset", "no-vat"],
            "motor_expenses": ["Motor Running Expenses", "overhead", "no-vat"],
            "capital": ["Capital", "equity", "no-vat"],
            "opening_balances": ["Opening Balances", "equity", "no-vat"],
            "inventory": ["Inventory", "inventory", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (purchases,        "154000", "2024-06-30", opening_balances),
        (rent,               "3800", "2024-06-30", opening_balances),
        (lighting_heating,    "700", "2024-06-30", opening_balances),
        (salaries_wages,    "52000", "2024-06-30", opening_balances),
        (insurance,          "3000", "2024-06-30", opening_balances),
        (buildings,         "84800", "2024-06-30", opening_balances),
        (fixtures,           "2000", "2024-06-30", opening_balances),
        (trade_receivables, "31200", "2024-06-30", opening_balances),
        (sundry_expenses,     "300", "2024-06-30", opening_balances),
        (bank,              "15000", "2024-06-30", opening_balances),
        (drawings,          "28600", "2024-06-30", opening_balances),
        (vans,              "16000", "2024-06-30", opening_balances),
        (motor_expenses,     "4600", "2024-06-30", opening_balances),
        (opening_balances, "266000", "2024-06-30", sales),
        (opening_balances,  "16000", "2024-06-30", trade_payables),
        (opening_balances, "114000", "2024-06-30", capital),
        (inventory,         "18000", "2024-06-30", opening_balances),
    ]]
    # fmt: on

    return ledger


def load_chapter_7_review_7_5():

    book = BookFactory()
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()
    # fmt: off
    bank, capital, loan, van_hire, it_equipment, purchases, \
        j_collins, e_barrett, m_pembridge, drawings, wages, inventory, \
        purchases_returns, sales, opening_balances = [
        coa.get_or_create(*args)
        for k, (args) in {
            "bank": ["Bank Account", "bank"],
            "capital": ["Capital", "equity", "no-vat"],
            "loan": ["LloydWest Bank Loan", "non-current-liability", "no-vat"],
            "van_hire": ["Van Hire", "overhead", "no-vat"],
            "it_equipment": ["IT Equipment", "non-current-asset", "no-vat"],
            "purchases": ["Purchases", "purchases"],
            "j_collins": ["J Collins", "accounts-payable", "no-vat"],
            "e_barrett": ["E Barrett", "accounts-receivable", "no-vat"],
            "m_pembridge": ["M Pembridge", "accounts-payable", "no-vat"],
            "drawings": ["Drawings", "equity", "no-vat"],
            "wages": ["Wages", "overhead", "no-vat"],
            "inventory": ["Inventory", "inventory", "no-vat"],
            "purchases_returns": ["Purchases Returns", "purchases-returns", "no-vat"],
            "sales": ["Sales", "sales"],
            "opening_balances": ["Opening Balances", "equity", "no-vat"],
        }.items()
    ]
    # fmt: on

    # fmt: off
    # debit acct, amount, date, credit account
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (bank,          "750", "2023-09-01", capital),
        (bank,         "3000", "2023-09-03", loan),
        (van_hire,      "320", "2023-09-05", bank),
        (it_equipment, "2200", "2023-09-07", bank),
        (purchases,     "760", "2023-09-09", bank),
        (purchases,     "570", "2023-09-11", j_collins),
        (bank,          "930", "2023-09-13", sales),
        (j_collins,     "120", "2023-09-15", purchases_returns),
        (purchases,     "890", "2023-09-17", m_pembridge),
        (e_barrett,    "1770", "2023-09-19", sales),
        (j_collins,     "450", "2023-09-21", bank),
        (bank,          "590", "2023-09-23", e_barrett),
        (drawings,      "280", "2023-09-25", bank),
        (wages,         "410", "2023-09-27", bank),
        # applied in the calculation of the trading account
        # (inventory,     "570", "2023-09-30", opening_balances),
    ]]
    # fmt: on

    return ledger
