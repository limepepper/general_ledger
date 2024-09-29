import factory
from general_ledger.models import Contact


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact
        # django_get_or_create = ("name",)

    name = factory.Faker("name")
    is_customer = factory.Faker("boolean", chance_of_getting_true=70)
    is_supplier = factory.Faker("boolean", chance_of_getting_true=30)
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    address = factory.Faker("address")

    @classmethod
    def customer(cls, **kwargs):
        kwargs.update({"is_customer": True, "is_supplier": False})
        return cls.create(**kwargs)

    @classmethod
    def supplier(cls, **kwargs):
        kwargs.update({"is_customer": False, "is_supplier": True})
        return cls.create(**kwargs)
