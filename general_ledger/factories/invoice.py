import random
from datetime import timedelta
from decimal import Decimal

import factory
from factory import SubFactory, LazyAttribute, post_generation
from factory.django import DjangoModelFactory

from general_ledger.models import Invoice, InvoiceLine
from general_ledger.models.tax_inclusive import TaxInclusive
from faker import Faker


def get_random_tax_rate_for_book(book):
    return random.choice(book.tax_rates.all().filter(tax_type__name="Sales"))


fake = Faker()


class InvoiceFactory(DjangoModelFactory):

    class Meta:
        model = Invoice
        skip_postgeneration_save = True
        # django_get_or_create = ("name",)

    ledger = SubFactory("general_ledger.factories.LedgerFactory")

    description = factory.Faker("sentence", nb_words=6)

    contact = factory.SubFactory(
        "general_ledger.factories.ContactFactory",
        book=factory.SelfAttribute("..ledger.book"),
        is_customer=True,
        is_supplier=False,
    )

    invoice_number = factory.LazyAttribute(
        lambda p: "{}{}".format(
            "INV-",
            fake.random_number(
                digits=6,
                fix_len=True,
            ),
        )
    )

    tax_inclusive = factory.LazyFunction(
        lambda: random.choice([choice.value for choice in TaxInclusive])
    )

    date = factory.Faker(
        "date_between",
        start_date="-2y",
        end_date="today",
    )

    due_date = factory.LazyAttribute(
        lambda con_factory: con_factory.date + timedelta(30)
    )

    total_amount = 0  # Initialize with 0

    # @classmethod
    # def _create(cls, model_class, *args, **kwargs):
    #     obj = super()._create(model_class, *args, **kwargs)
    #     num_lines = random.randint(1, 10)
    #     InvoiceLineFactory.create_batch(num_lines, invoice=obj)
    #     obj.total_amount = sum(line.total for line in obj.lines.all())
    #     obj.save()
    #     return obj

    @post_generation
    def create_invoice_lines(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted == []:
            return

        num_lines = random.randint(1, 5)
        InvoiceLineFactory.create_batch(num_lines, invoice=self)


class InvoiceLineFactory(DjangoModelFactory):
    class Meta:
        model = InvoiceLine

    invoice = factory.SubFactory(
        "general_ledger.factories.InvoiceFactory",
    )
    description = factory.Faker("sentence", nb_words=6)
    quantity = LazyAttribute(lambda _: random.randint(1, 10))
    # unit_price = factory.Faker(
    #     "pydecimal", left_digits=3, right_digits=2, positive=True
    # )
    vat_rate = LazyAttribute(
        lambda o: o.invoice.ledger.book.taxrate_set.filter(tax_type__name="Sales")
        .order_by("?")
        .first()
    )

    @factory.lazy_attribute
    def unit_price(self):
        pounds = random.randint(1, 100) * 5
        pence_options = [0, 25, 50, 75, 99]
        pence_probabilities = [0.35, 0.25, 0.20, 0.15, 0.5]  # These should sum to 1
        pence = random.choices(pence_options, weights=pence_probabilities)[0]

        return Decimal(f"{pounds}.{pence:02d}")
