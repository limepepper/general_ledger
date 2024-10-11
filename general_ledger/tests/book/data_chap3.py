import logging

import pytest

from general_ledger.factories import BookFactory, LedgerFactory
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.django.models import (
    Transaction,
    Account,
    Entry,
)
from general_ledger.utils.data_loader import tx


def load_chapter_3_data():
    """
    1. Started a household machines business putting £2 ,000 into a
    bank account.
    2. Bought equipment on time from house supplies £12,000.


    """
    book = BookFactory(name="B. Swift")
    ledger = book.get_default_ledger()
    coa = book.get_default_coa()

    # fmt: off
    purchases, sales, cash, capital, sales_returns, purchases_returns, d_small, a_lyon, d_hughes, m_spencer = [
        coa.get_or_create(*args)
        for k, (args) in {
            "purchases": ["Purchases", "direct-costs"],
            "sales": ["Sales", "sales", "20-vat-on-income"],
            "cash": ["Cash", "cash", "no-vat"],
            "capital": ["Capital", "equity", "no-vat"],
            "sales_returns": ["Sales Returns", "current-asset", "20-vat-on-income"],
            "purchases_returns": ["Purchases Returns", "current-liability", "no-vat"],
            "d_small": ["D Small", "accounts-payable", "no-vat"],
            "a_lyon": ["A Lyon & Son", "accounts-payable", "no-vat"],
            "d_hughes": ["D Hughes", "accounts-receivable", "no-vat"],
            "m_spencer": ["M Spencer", "accounts-receivable", "no-vat"],
        }.items()
    ]
    # fmt: on



    # fmt: off
    txs = [tx(ledger, dr,amt,dt,cr) for dr,amt,dt,cr in [
        (purchases, "220", "2020-05-1", d_small),
        (purchases, "410", "2020-5-2", a_lyon),
        (d_hughes, "60.00", "2020-5-5", sales),
        (m_spencer, "45.00", "2020-5-6", sales),
        (d_small, "15.00", "2020-5-10", purchases_returns),
        (cash, "210.00", "2020-5-11", sales),
        (purchases, "150.00", "2020-5-12", cash),
        (sales_returns, "16.00", "2020-5-19", m_spencer),
        (cash, "175", "2020-5-21", sales),
        (d_small, "205", "2020-5-22", cash),
        (cash, "60", "2020-5-30", d_hughes),
        (purchases, "214", "2020-5-31", a_lyon)
    ]]
    # fmt: on

    return ledger
