from datetime import timezone, datetime

from django.db import models
from rich.console import Console
from rich.console import ConsoleOptions, RenderResult
from rich.table import Table

from general_ledger.render.utility_rich import model_table_generator


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

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from model_table_generator(self, self.model)


class InvoiceManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "contact",
        )
