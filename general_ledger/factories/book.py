import factory
from django.contrib.auth import get_user_model
from factory import post_generation, SubFactory
from faker import Faker

from general_ledger.models import Book
import sys

fake = Faker()


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book
        skip_postgeneration_save = True
        django_get_or_create = ("name",)

    name = factory.Faker("company")

    # owner = factory.LazyAttribute(
    #     lambda a: get_user_model().objects.get(username="admin")
    # )
    owner = SubFactory("general_ledger.factories.UserFactory")

    @post_generation
    def init_data(self, create, extracted, **kwargs):
        if not create:
            return
        self.initialize()
