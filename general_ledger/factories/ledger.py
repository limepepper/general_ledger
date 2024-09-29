import factory
from factory import SubFactory
from faker import Faker

from general_ledger.models import Ledger

fake = Faker()


class LedgerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ledger
        django_get_or_create = ("name",)

    name = factory.Faker("company")
    book = SubFactory("general_ledger.factories.BookFactory")
    # coa = book.get_default_coa()
    coa = factory.LazyAttribute(lambda a: a.book.get_default_coa())
