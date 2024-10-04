import random
from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory as DjangoModelFactory
from faker import Faker

from general_ledger.models import BankStatementLine
from general_ledger.models.bank_statement_line_type import BankStatementLineType

fake = Faker()


class BankTransactionFactory(DjangoModelFactory):
    class Meta:
        model = BankStatementLine

    bank = factory.SubFactory(
        "general_ledger.factories.BankAccountFactory",
    )

    date = factory.Faker("date_this_year")

    @factory.lazy_attribute
    def type(self):
        return random.choices(
            [e[0] for e in BankStatementLineType.choices],
            weights=[0.8]
            + [0.2 / (len(BankStatementLineType.choices) - 1)]
            * (len(BankStatementLineType.choices) - 1),
        )[0]

    amount = factory.LazyAttribute(
        lambda o: fake.pydecimal(
            left_digits=3,
            right_digits=2,
            positive=o.type
            in [
                BankStatementLineType.CREDIT,
                BankStatementLineType.INT,
                BankStatementLineType.DIV,
                BankStatementLineType.DEP,
                BankStatementLineType.DIRECTDEP,
            ],
        )
    )

    name = factory.LazyAttribute(lambda _: fake.bs().capitalize())

    @classmethod
    def create_transfer(
        cls,
        bank_from,
        bank_to,
        amount,
        date=None,
    ):
        if date is None:
            date = datetime.now()
        transaction_from = cls.create(
            bank=bank_from,
            amount=-amount,
            date=date,
            type=BankStatementLineType.XFER,
            name="To A/C " + bank_to.account_number,
            ofx_memo=bank_to.book.name,
        )

        transaction_to = cls.create(
            bank=bank_to,
            amount=amount,
            date=date,
            type=BankStatementLineType.XFER,
            name="From A/C " + bank_from.account_number,
            ofx_memo=bank_from.book.name,
        )

        return transaction_from, transaction_to

    @classmethod
    def create_transfers(
        cls,
        num_transactions,
        banks,
        years_ago=3,
        description="Bank Transfer",
        banks_to=None,
    ):
        """
        Creates parameterized bank transfers between two or more banks.

        Args:
            banks (list): A list of Bank objects to create transfers between.
            num_transactions (int): The number of transactions to create.
            years_ago (int, optional): The maximum number of years ago for transaction dates. Defaults to 3.
            description (str, optional): Description for the bank transfers. Defaults to "Bank Transfer".

        Returns:
            list: A list of created BankStatementLine objects.
        """
        fake = Faker()
        created_transactions = []

        for _ in range(num_transactions):

            if banks_to:
                bank_from = fake.random.choice(banks)
                bank_to = fake.random.choice(banks_to)
            else:
                bank_from, bank_to = fake.random.sample(banks, 2)

            if bank_from == bank_to:
                raise ValueError("Cannot transfer to the same bank")

            transaction_date = fake.date_between(
                start_date=datetime.now() - timedelta(days=years_ago * 365),
                end_date="today",
            )

            amount = fake.pydecimal(
                left_digits=3,
                right_digits=2,
                positive=True,
            )

            transaction_from, transaction_to = cls.create_transfer(
                bank_from,
                bank_to,
                amount,
                date=transaction_date,
            )
            created_transactions.append(transaction_from)
            created_transactions.append(transaction_to)

        return created_transactions

    @classmethod
    def create_with_transactions(cls, bank_from, bank_to, **kwargs):
        amount = factory.Faker(
            "pydecimal", left_digits=3, right_digits=2, positive=True
        )

        xfers_from = BankTransactionFactory.create_batch(
            10,
            bank=bank_from,
            amount=0 - amount,
        )

        xfers_to = BankTransactionFactory.create_batch(
            10,
            bank=bank_to,
            amount=amount,
        )
        return xfers_from + xfers_to

    # @classmethod
    # def _create(cls, model_class, *args, **kwargs):
    #     """
    #     Override the default _create method of the DjangoModelFactory
    #     :param model_class:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     # We need to pop the 'author' key from the kwargs dictionary
    #     # author = kwargs.pop('author')
    #     # Now we can call the default _create method
    #     obj = super(InvoiceFactory, cls)._create(model_class, *args, **kwargs)
    #     # Finally, we can assign the author to the created object
    #     # obj.author.add(author)
    #     return obj
