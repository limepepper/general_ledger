import logging

import pytest

from general_ledger.factories import BookFactory, LedgerFactory
from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.django.models import (
    Transaction,
    Account,
    Entry,
)
from general_ledger.tests.book.data_chap3 import load_chapter_3_data
from general_ledger.utils.data_loader import tx


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
