import pytest
from django.db.models import Q
from rich import inspect

from general_ledger.factories import BookFactory, BankAccountFactory
from general_ledger.factories.bank_transactions import BankTransactionFactory
from general_ledger.helpers.matcher import MatcherHelper
from general_ledger.models import Bank, Payment


class TestPaymentSearching():
    @pytest.mark.django_db
    def test_search_payments(self):
        book = BookFactory()
        bank_1 = BankAccountFactory(type=Bank.CHECKING, book=book)
        bank_2 = BankAccountFactory(type=Bank.SAVINGS, book=book)
        txs = BankTransactionFactory.create_transfers(
            2,
            banks=[bank_1],
            banks_to=[bank_2],
        )
        #inspect(txs, title="txs")
        matcher = MatcherHelper(bank=bank_1)
        matcher.reconcile_bank_statement()
        #inspect(matcher, title="matcher")
        matcher.process_matches()

        #inspect(matcher, title="matcher")
        #inspect(Payment.objects.all(), title="payments")

        qs = Payment.objects.filter(
            Q(items__from_object_id__in=bank_1.bankstatementline_set.values_list('id', flat=True)) |
            Q(items__to_object_id__in=bank_2.bankstatementline_set.values_list('id', flat=True))
        )
        print(qs.query)
        #inspect(qs, title="payments")
        assert qs.count() == 2

