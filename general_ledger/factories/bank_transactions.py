import factory
import random
from datetime import timedelta
import factory
from factory import SubFactory, LazyFunction, LazyAttribute, Faker, post_generation
from factory.django import DjangoModelFactory as DjangoModelFactory
from factory.fuzzy import FuzzyDecimal

from general_ledger.models import Invoice, InvoiceLine, TaxRate, BankStatementLine
from general_ledger.models.tax_inclusive import TaxInclusive


class BankTransactionFactory(DjangoModelFactory):
    class Meta:
        model = BankStatementLine

    bank = factory.SubFactory("general_ledger.factories.BankAccountFactory")
    # description = factory.Faker("sentence", nb_words=6)
    # payee = factory.Faker(
    #     "random_number",
    #     digits=8,
    #     fix_len=True,
    # )
    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    date = factory.Faker("date_this_year")

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
