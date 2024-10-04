import datetime
import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import is_aware
from loguru import logger
from rich import inspect
from timezone_field import TimeZoneField

from general_ledger.managers.bank import BankManager
from general_ledger.managers.bank_statement_line import (
    BankStatementLineManager,
    BankStatementLineManagerQuerySet,
)
from general_ledger.models.mixins import LinksMixin
from general_ledger.models.mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
)
from general_ledger.models.payment import Payment

from django.db.models import Q


class BankStatementLine(
    UuidMixin,
    CreatedUpdatedMixin,
    # SlugMixin,
    LinksMixin,
):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    objects = BankStatementLineManager.from_queryset(
        queryset_class=BankStatementLineManagerQuerySet
    )()

    class Meta:
        db_table = "gl_bank_statement_line"
        verbose_name = "Bank Statement Line"
        verbose_name_plural = "Bank Statement Lines"
        ordering = [
            "date",
            "index",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["bank", "date", "index"],
                name="bankstatementline_uniq_bank_date_index",
            )
        ]

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

    bank = models.ForeignKey(
        "Bank",
        on_delete=models.CASCADE,
    )

    """
    this is the timezone of the date of the transaction, either from
    the transaction, if it was provided, or the timezone of the bank
    account if it was not. The date itself is persisted in UTC
    so this is needed to resolve back to the timezoned date.
    """
    tz = TimeZoneField(default="Europe/London")

    # a bare date is generally provided by bank statements
    # however payment providers may provide a datetime
    date = models.DateField()
    datetime = models.DateTimeField()

    amount = models.DecimalField(
        max_digits=16,
        decimal_places=4,
    )

    type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ofx_fitid = models.CharField(
        max_length=255,
        blank=True,
    )

    ofx_name = models.CharField(
        max_length=255,
        blank=True,
    )

    ofx_memo = models.CharField(
        max_length=255,
        blank=True,
    )

    ofx_dtposted = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )

    ofx_trntype = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=255,
        # db_comment="This field is used to store the description, or payee of the transaction. It is confusingly called 'name' by the OFX specification.",
        help_text="This is the description of the transaction. It is confusingly called 'name' by the OFX specification. It is populated from the description when provided",
    )

    payee = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # this badly named field is for tracaking FITID in OFX
    transaction_id = models.CharField(
        max_length=124,
        null=True,
        blank=True,
    )

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

    # some formats don't track balance per line
    balance = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        null=True,
        blank=True,
    )

    # link back to the payment
    payments_to = GenericRelation(
        "PaymentItem",
        related_query_name="bank_transaction_from",
        content_type_field="from_content_type",
        object_id_field="from_object_id",
    )
    payments_from = GenericRelation(
        "PaymentItem",
        related_query_name="bank_transaction_to",
        content_type_field="to_content_type",
        object_id_field="to_object_id",
    )

    # this is a flag to indicate that the transaction has been matched
    # to a candidate transaction in the system. however the user can
    # still choose to unmatch and reconcile the transaction otherwise.
    is_matched = models.BooleanField(default=False)
    is_reconciled = models.BooleanField(default=False)

    def reconcile(self):
        self.is_reconciled = True
        self.save()

    def get_payments(self):
        distinct_payments = Payment.objects.filter(
            Q(items__from_object_id=self.id) | Q(items__to_object_id=self.id)
        ).distinct()
        return distinct_payments

    # calculate hash if not provided
    def save(self, *args, **kwargs):
        logger.trace(f"BankTransaction: [saving] {self._state}")

        if self._state.adding:
            if not self.date and not self.datetime:
                raise ValidationError("BankStatementLine must have a date or datetime")
            if self.datetime and not self.date:
                if is_aware(self.datetime):
                    self.tz = self.datetime.tzinfo
                else:
                    self.tz = self.bank.tz
                self.date = self.datetime.date()

            elif self.date and not self.datetime:
                self.datetime = datetime.datetime(self.date.year, self.date.month, self.date.day, tzinfo=self.bank.tz,)

            if not self.hash:
                self.hash = self.get_hash()
                logger.trace("BankTransaction: [hash] {self.hash}")

            if not self.index:
                logger.trace(f"BankStatementLine adding index: {self}")
                last_index = BankStatementLine.objects.filter(
                    bank=self.bank, date=self.date
                ).aggregate(models.Max("index"))["index__max"]
                self.index = last_index + 1 if last_index is not None else 1

        try:
            self.full_clean()
        except ValidationError as e:
            inspect(self)
            raise e

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
