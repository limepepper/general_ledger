import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from general_ledger.models.payment import Payment
from general_ledger.models.mixins import LinksMixin
from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
)
from loguru import logger


class BankStatementLine(
    UuidMixin,
    CreatedUpdatedMixin,
    # SlugMixin,
    LinksMixin,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    # generic view class attributes
    links_detail = "general_ledger:bank-transaction-detail"
    links_list = "general_ledger:bank-transactions-list"
    links_create = "general_ledger:bank-transaction-create"
    links_edit = "general_ledger:bank-transaction-update"
    links_title_field = "name"

    generic_list_display = (
        "link",
        "type",
        "hash",
        "amount",
    )

    # # generic view class attributes
    # links_detail = "general_ledger:bank-statement-detail"
    # links_list = "general_ledger:bank-statement-list"
    # links_create = "general_ledger:bank-statement-create"
    # links_edit = "general_ledger:bank-statement-update"
    # links_title_field = "name"
    #
    # generic_list_display = (
    #     "link",
    #     "type",
    #     "account_number",
    #     "sort_code",
    # )

    bank = models.ForeignKey(
        "Bank",
        on_delete=models.CASCADE,
    )

    date = models.DateField()

    name = models.CharField(
        max_length=255,
        # db_comment="This field is used to store the description, or payee of the transaction. It is confusingly called 'name' by the OFX specification.",
        help_text="This is the description of the transaction. It is confusingly called 'name' by the OFX specification. It is populated from the description when provided",
    )
    payee = models.CharField(max_length=255, null=True, blank=True)

    # this field is for creating a canonical hash for the transaction
    # to allow comparing across different sources.
    hash = models.CharField(
        max_length=50,
        blank=True,
    )

    # disambiguate the transaction for clashing hash, date and amount
    index = models.PositiveIntegerField(
        default=0,
    )

    amount = models.DecimalField(max_digits=16, decimal_places=4)

    # some formats don't track balance per line
    balance = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True
    )

    # this badly named field is for tracaking FITID in OFX
    transaction_id = models.CharField(max_length=124, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    # this is a flag to indicate that the transaction has been matched
    # to a candidate transaction in the system. however the user can
    # still choose to unmatch and reconcile the transaction otherwise.
    is_matched = models.BooleanField(default=False)
    is_reconciled = models.BooleanField(default=False)

    def reconcile(self):
        self.is_reconciled = True
        self.save()

    payments_to = GenericRelation(
        "PaymentItem",
        related_query_name="bank_transaction_from",
        content_type_field="from_content_type",
        object_id_field="from_object_id",
    )

    def get_payments(self):
        distinct_payments = Payment.objects.filter(
            items__from_object_id=self.id
        ).distinct()
        return distinct_payments

    class Meta:
        db_table = "gl_bank_statement_line"
        verbose_name = "Bank Statement Line"
        verbose_name_plural = "Bank Statement Lines"
        ordering = ["date", "name"]

    # calculate hash if not provided
    def save(self, *args, **kwargs):
        logger.trace(f"BankTransaction: [saving] {self._state}")

        if self._state.adding:
            if not self.hash:
                self.hash = self.get_hash()
                logger.trace("BankTransaction: [hash] {self.hash}")

        super().save(*args, **kwargs)

    # @TODO this is a bit of a hack to get around the fact that
    # the tests are not using the same hash function as the model
    def get_hash(self):
        return self.name[:32]

    def __str__(self):
        return f"{self.date}:{self.name}:{self.type}:[{self.amount}]"

    def get_credit_amount(self):
        return abs(self.amount) if self.amount < 0 else 0

    def get_debit_amount(self):
        return self.amount if self.amount > 0 else 0
