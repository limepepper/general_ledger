import pytest

from general_ledger.factories import BankAccountFactory
from general_ledger.models import Bank


class TestBankAccountManager:
    @pytest.mark.django_db
    def test_fuzzy_search(self):
        BankAccountFactory(
            name="Bank of America",
            type=Bank.CHECKING,
        )

        result = Bank.objects.search("bank")

        assert isinstance(result, Bank)

        bank = BankAccountFactory(
            type=Bank.CHECKING,
        )

        result = Bank.objects.search(bank.slug)

        assert isinstance(result, Bank)

        result = Bank.objects.search(str(bank.id))

        assert isinstance(result, Bank)

        bank = BankAccountFactory(
            id="96341e4a-b1b2-494d-908b-124eaa7c887f",
        )

        result = Bank.objects.search(
            "96341e4a-b1b2-494d-908b-124eaa7c887f",
        )

        assert isinstance(result, Bank)
