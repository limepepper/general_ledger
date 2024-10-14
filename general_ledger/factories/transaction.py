import random
from decimal import Decimal

import factory
from factory import post_generation
from factory.django import DjangoModelFactory
from faker import Faker
from rich import inspect

from general_ledger.factories.ledger import LedgerFactory
from general_ledger.models import Transaction, Entry, Direction

fake = Faker()


class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Transaction
        skip_postgeneration_save = True

    ledger = factory.SubFactory(LedgerFactory)
    description = factory.Faker("sentence")

    trans_date = factory.Faker(
        "date_between",
        start_date="-2y",
        end_date="today",
    )

    # @classmethod
    # def create(cls, **kwargs):
    #     accounts_data = kwargs.pop("accounts", [])
    #     if accounts_data:
    #         inspect(accounts_data)
    #
    #         kwargs["account"] = random.choice(accounts_data)
    #
    #         # kwargs["account"] = AccountFactory(**kwargs["account"])
    #     return super().create(**kwargs)

    @post_generation
    def create_transaction_entry_lines(
        self, create, extracted, accounts=None, balanced=True, **kwargs
    ):
        if not create:
            return
        # print(f"Extracted: {extracted}")
        if extracted == []:
            return

        num_entries = random.randint(2, 5)

        entries = TransactionEntryFactory.create_batch(
            num_entries - 1,
            transaction=self,
            accounts=accounts,
        )

        total_debit = sum(
            entry.amount for entry in entries if entry.tx_type == Direction.DEBIT
        )
        total_credit = sum(
            entry.amount for entry in entries if entry.tx_type == Direction.CREDIT
        )

        # Create the final entry to balance or intentionally unbalance
        last_entry = TransactionEntryFactory.create(
            transaction=self,
            amount=(
                abs(total_credit - total_debit)
                if balanced
                else abs(total_credit - total_debit) + Decimal("0.01")
            ),
            tx_type=Direction.DEBIT if total_credit > total_debit else Direction.CREDIT,
            accounts=accounts,
        )
        entries.append(last_entry)


class TransactionEntryFactory(DjangoModelFactory):
    class Meta:
        model = Entry

    transaction = factory.SubFactory("general_ledger.factories.TransactionFactory")

    # account = factory.SubFactory(
    #     "general_ledger.factories.AccountFactory",
    #     coa=factory.SelfAttribute(
    #         "..transaction.ledger.coa"
    #     ),  # Access from transaction
    # )
    account = factory.LazyAttribute(
        lambda o: random.choice(o.transaction.ledger.coa.account_set.all()),
    )
    description = factory.Faker("sentence")
    amount = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
    )
    tx_type = factory.LazyAttribute(
        lambda o: o.account.type.direction
    )  # Set based on account type

    @classmethod
    def create(cls, **kwargs):
        accounts_data = kwargs.pop("accounts", [])
        if accounts_data:
            # inspect(accounts_data)

            kwargs["account"] = random.choice(accounts_data)

            # kwargs["account"] = AccountFactory(**kwargs["account"])
        return super().create(**kwargs)
