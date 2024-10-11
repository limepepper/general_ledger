from random import randint

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from general_ledger.factories.account_factory import AccountFactory
from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.factories.faker_utils import rand_sort_code, suffixes
from general_ledger.models import Bank

fake = Faker()


class BankAccountFactory(DjangoModelFactory):
    class Meta:
        model = Bank
        # django_get_or_create = ("name",)

    book = factory.SubFactory("general_ledger.factories.book.BookFactory")

    name = factory.LazyAttribute(
        lambda p: "{} {}".format(fake.company(), fake.random_element(elements=suffixes))
    )

    account_number = factory.LazyAttribute(
        lambda _: f"{fake.random_number(digits=8, fix_len=True):08d}"
    )

    sort_code = factory.LazyAttribute(rand_sort_code)

    type = factory.Faker(
        "random_element", elements=[choice for choice in Bank.TYPE_CHOICES]
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):

        account_data = {}

        if "account" in kwargs:
            account_data = kwargs.pop("account")
            if isinstance(account_data, AccountFactory):
                account_data = account_data.build().__dict__

        return Bank.objects.create_with_account(*args, **kwargs, **account_data)

    @classmethod
    def create(cls, **kwargs):
        if "account" in kwargs and isinstance(kwargs["account"], dict):
            kwargs["account"] = AccountFactory(**kwargs["account"])
        return super().create(**kwargs)

    @classmethod
    def create_with_transactions(cls, num_transactions=0, **kwargs):
        bank = cls.create(**kwargs)
        BankTransactionFactory.create_batch(
            num_transactions,
            bank=bank,
        )
        return bank
