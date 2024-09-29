from random import randint

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from general_ledger.factories.account import AccountFactory
from general_ledger.models import Bank


def rand_sort_code(_):
    return f"{randint(0, 99):02d}-{randint(0, 99):02d}-{randint(0, 99):02d}"


suffixes = [
    "Bank",
    "National Bank",
    "Savings and Loans",
    "Mutual",
    "Credit Union",
]


def rand_bankish_name():
    return f"{factory.Faker('company')} {factory.Faker('random_element',  elements=suffixes)}"


fake = Faker()


class BankAccountFactory(DjangoModelFactory):
    class Meta:
        model = Bank
        # django_get_or_create = ("name",)

    name = factory.LazyAttribute(
        lambda p: "{} {}".format(fake.company(), fake.random_element(elements=suffixes))
    )

    account_number = factory.Faker(
        "random_number",
        digits=8,
        fix_len=True,
    )
    # sort_code = factory.LazyAttribute(
    #     lambda _: f"{factory.Faker('random_number', digits=2, fix_len=True)}"
    # )
    sort_code = factory.LazyAttribute(rand_sort_code)

    book = factory.SubFactory("general_ledger.factories.book.BookFactory")

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
