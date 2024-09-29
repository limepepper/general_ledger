from datetime import datetime

import factory

from general_ledger.factories.book import BookFactory
from general_ledger.factories.ledger import LedgerFactory
from general_ledger.models import Transaction


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    ledger = factory.SubFactory(LedgerFactory)
    description = factory.Faker("sentence")

    trans_date = factory.Faker(
        "date_between",
        start_date=datetime(year=2022, month=1, day=1).date(),
        end_date=datetime.now().date(),
    )

    book = factory.SubFactory(BookFactory)
