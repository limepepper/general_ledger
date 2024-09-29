from uuid import UUID

from django.db import models
from django.db.models import Q


class BookQuerySet(models.QuerySet):
    def demo(self):
        return self.filter(is_demo=True)


class BookManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "owner",
        )

    def for_user(self, user):
        return self.get_queryset().filter(
            Q(owner=user) | Q(users__in=[user]),
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            pk=book.pk,
        )

    def get_fuzzy(self, value):
        # Try to convert the value to UUID
        try:
            uuid_value = UUID(value)
            is_valid_uuid = True
        except (ValueError, TypeError) as e:
            is_valid_uuid = False

        # Create a Q object with multiple conditions
        filter_condition = Q(name__iexact=value) | Q(slug__iexact=value)

        # Add UUID condition if the value is a valid UUID
        if is_valid_uuid:
            filter_condition |= Q(pk=uuid_value)

        # Apply the filter to the queryset
        return self.get_queryset().get(filter_condition)

    def get_by_natural_key(self, owner, slug):
        return self.get(
            owner=owner,
            slug=slug,
        )
