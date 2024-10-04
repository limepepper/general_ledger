from bs4 import BeautifulSoup as bs
from django.test import TestCase
from rich import inspect

from general_ledger.factories import BookFactory
from general_ledger.forms.bank import BankForm
from general_ledger.models import Bank, Account


class AddBankFormTests(TestCase):
    def test_bank_form_simplez(self):
        book = BookFactory()
        request = type("", (), {})()
        setattr(request, "active_book", book)
        create_form = BankForm(
            data={
                "name": "A bank name",
                "account_number": "98765432",
                "sort_code": "12-34-45",
                "type": Bank.CHECKING,
                "is_active": True,
            },
            request=request,
        )

        inspect(create_form)

        new_bank = create_form.save()
        new_bank_from_query = Bank.objects.get(name="A bank name")
        assert new_bank == new_bank_from_query
        assert Bank.objects.count() == 1

        new_account = new_bank.account
        new_account_from_query = Account.objects.get(name="A bank name")
        assert new_account == new_account_from_query
        assert new_account.name == "A bank name"
        assert new_account.tax_rate.slug == "no-vat"

        update_form = BankForm(
            {
                "name": "A new bank name",
                "account_number": "98765432",
                "sort_code": "12-34-45",
                "type": Bank.CHECKING,
            },
            instance=new_bank,
            request=request,
        )

        updated_bank = update_form.save()
        assert updated_bank.name == "A new bank name"
        updated_bank_from_query = Bank.objects.get(name="A new bank name")
        assert updated_bank == updated_bank_from_query
        assert Bank.objects.count() == 1
        updated_account = updated_bank.account
        updated_account_from_query = Account.objects.get(name="A new bank name")
        assert updated_account == updated_account_from_query
        assert updated_account.name == "A new bank name"
