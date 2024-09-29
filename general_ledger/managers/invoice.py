from datetime import timezone, datetime

from django.db import models


class InvoiceQuerySet(models.QuerySet):
    def for_contact(self, contact):
        return self.filter(
            contact=contact,
        )

    def for_book(self, book):
        return self.filter(
            ledger__book=book,
        )

    def for_ledger(self, ledger):
        return self.filter(
            ledger=ledger,
        )

    def for_user(self, user):
        return self.filter(
            ledger__book__owner=user,
        )

    def awaiting_payment(self):
        return self.filter(
            status=self.model.InvoiceStatus.AWAITING_PAYMENT,
        )

    def overdue(self):
        return self.filter(
            status=self.model.InvoiceStatus.AWAITING_PAYMENT,
            due_date__lt=datetime.today(),
        )


class InvoiceManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "contact",
        )
