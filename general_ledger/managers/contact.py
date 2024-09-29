from django.db import models


class ContactQuerySet(models.QuerySet):
    def customers(self):
        return self.filter(
            is_customer=True,
        )

    def suppliers(self):
        return self.filter(
            is_supplier=True,
        )


class ContactManager(models.Manager):
    # @TODO if this can be done in the queryset, then do it there
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )

    def get_by_natural_key(self, name, book):
        return self.get(
            name=name,
            book=book,
        )
