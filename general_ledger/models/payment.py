from django.db import models
from loguru import logger
from xstate_machine import FSMField, transition

from general_ledger.helpers.payment import PaymentHelper
from general_ledger.managers.payment import PaymentManager
from general_ledger.models.document_status import DocumentStatus
from general_ledger.models.mixins import (
    LinksMixin,
    ValidatableModelMixin,
    EditableMixin,
)
from general_ledger.models.mixins import UuidMixin, CreatedUpdatedMixin


class Payment(
    UuidMixin,
    CreatedUpdatedMixin,
    LinksMixin,
    ValidatableModelMixin,
    EditableMixin,
):
    """
    A payment is a document of a transfer that links a bank transaction to an invoice, or between other
    financial documents
    """

    objects = PaymentManager()

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        db_table = "gl_payment"
        ordering = ["-created_at"]

    # generic view class attributes
    links_detail = "general_ledger:payment-detail"
    links_list = "general_ledger:payments-list"
    links_create = "general_ledger:payment-create"
    links_edit = "general_ledger:payment-update"
    links_title_field = "name"

    ledger = models.ForeignKey(
        "Ledger",
        on_delete=models.CASCADE,
    )

    date = models.DateField()
    amount = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        default=0.0000,
    )

    is_posted = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    state = FSMField(
        default=DocumentStatus.DRAFT,
        choices=DocumentStatus.choices,
        # protected=True,
    )

    transactions = models.ManyToManyField(
        "Transaction",
        related_name="payments",
        through="PaymentTransaction",
    )

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"Payment {self.date} {self.amount} {self.state}"

    #
    ## Do custom handling stuff upon saving an invoice
    #
    def save(self, *args, **kwargs):
        logger.trace(f"Payment: [saving] {self._state}")
        self.recalculate_total()
        super().save(*args, **kwargs)

    def recalculate_total(self):
        try:
            self.amount = sum(line.amount for line in self.items.all())
        except Exception as e:
            logger.error(f"error calculating total amount {e}")

    def can_edit(self):
        return all(
            [
                not self.is_locked,
                DocumentStatus(self.state) == DocumentStatus.DRAFT,
            ]
        )

    def is_draft(self):
        return self.state == DocumentStatus.DRAFT

    def is_recorded(self):
        return self.state == DocumentStatus.RECORDED

    def promote(self):
        if self.state == DocumentStatus.DRAFT:
            self.to_state_recorded()
        elif self.state == DocumentStatus.RECORDED:
            self.to_state_posted()
        elif self.state == DocumentStatus.POSTED:
            self.to_state_complete()
        else:
            logger.warning(f"Payment {self.id} is already complete")
            raise Exception(f"Payment {self.id} is already complete")
        self.save()

    def demote(self):
        if self.state == DocumentStatus.COMPLETE:
            self.to_state_uncomplete()
        elif self.state == DocumentStatus.POSTED:
            self.to_state_unposted()
        elif self.state == DocumentStatus.RECORDED:
            self.to_state_unrecorded()
        else:
            logger.warning(f"Payment {self.id} is already in draft")
            raise Exception(f"Payment {self.id} is already in draft")
        self.save()

    def next_status(self):
        if self.state == DocumentStatus.DRAFT:
            return DocumentStatus.RECORDED
        elif self.state == DocumentStatus.RECORDED:
            return DocumentStatus.POSTED
        elif self.state == DocumentStatus.POSTED:
            return DocumentStatus.COMPLETE
        else:
            return None

    def prev_status(self):
        if self.state == DocumentStatus.COMPLETE:
            return DocumentStatus.POSTED
        elif self.state == DocumentStatus.POSTED:
            return DocumentStatus.RECORDED
        elif self.state == DocumentStatus.RECORDED:
            return DocumentStatus.DRAFT
        else:
            return None

    @transition(
        field=state,
        source=[
            DocumentStatus.DRAFT,
        ],
        target=DocumentStatus.RECORDED,
    )
    def to_state_recorded(self):
        payment_helper = PaymentHelper(self)
        payment_helper.create_related_records()

    @transition(
        field=state,
        source=[
            DocumentStatus.RECORDED,
        ],
        target=DocumentStatus.POSTED,
    )
    def to_state_posted(self):
        payment_helper = PaymentHelper(self)
        payment_helper.post_related_records()

    @transition(
        field=state,
        source=[
            DocumentStatus.POSTED,
        ],
        target=DocumentStatus.COMPLETE,
    )
    def to_state_complete(self):
        payment_helper = PaymentHelper(self)
        payment_helper.reconcile_related_records()

    @transition(
        field=state,
        source=[
            DocumentStatus.COMPLETE,
        ],
        target=DocumentStatus.POSTED,
    )
    def to_state_uncomplete(self):
        payment_helper = PaymentHelper(self)
        payment_helper.unreconcile_related_records()

    @transition(
        field=state,
        source=[
            DocumentStatus.POSTED,
        ],
        target=DocumentStatus.RECORDED,
    )
    def to_state_unposted(self):
        payment_helper = PaymentHelper(self)
        payment_helper.unpost_related_records()

    @transition(
        field=state,
        source=[
            DocumentStatus.RECORDED,
        ],
        target=DocumentStatus.DRAFT,
    )
    def to_state_unrecorded(self):
        payment_helper = PaymentHelper(self)
        payment_helper.delete_related_records()
