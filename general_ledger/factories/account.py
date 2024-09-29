from factory import LazyAttribute
from factory.django import DjangoModelFactory

from general_ledger.models import Account


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account

    coa = LazyAttribute(lambda o: o.book.get_default_coa())
    tax_rate = LazyAttribute(
        lambda o: o.invoice.ledger.book.taxrate_set.filter(tax_type__name="Sales")
        .order_by("?")
        .first()
    )
    account_type = LazyAttribute(
        lambda o: o.book.accounttype_set.get(account_type__name="Bank")
    )
