import factory
from factory import LazyAttribute
from factory.django import DjangoModelFactory

from general_ledger.models import Account
from factory import post_generation, SubFactory


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account

    # @TODO this ???
    name = LazyAttribute(lambda o: o.book.get_random_account_name())
    name = factory.Faker("company")
    coa = LazyAttribute(lambda o: o.book.get_default_coa())
    tax_rate = LazyAttribute(
        lambda o: o.coa.book.taxrate_set.all().order_by("?").first()
    )
    type = LazyAttribute(lambda o: o.coa.book.accounttype_set.get(name="Bank"))
