from datetime import datetime

from django.db import models

from general_ledger.models.document_status import DocumentStatus
from general_ledger.models.invoice_base import InvoiceBaseMixin

from xstate_machine import FSMField, transition


class BillManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "contact",
        )

    def for_contact(self, contact):
        return self.get_queryset().filter(
            contact=contact,
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            ledger__book=book,
        )

    def for_ledger(self, ledger):
        return self.filter(
            ledger=ledger,
        )

    def overdue(self):
        return self.filter(
            status=self.model.InvoiceStatus.AWAITING_PAYMENT,
            due_date__lt=datetime.today(),
        )


class PurchaseInvoice(InvoiceBaseMixin):

    class Meta:
        verbose_name = "Bill"
        verbose_name_plural = "Bills"
        db_table = "gl_bill"

    objects = BillManager()

    state = FSMField(
        default=DocumentStatus.DRAFT,
        choices=DocumentStatus.choices,
        # protected=True,
    )

    def can_edit(self):
        return all(
            [
                DocumentStatus(self.state) == DocumentStatus.DRAFT,
                not self.is_locked,
            ]
        )
