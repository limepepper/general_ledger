import logging

from django.db.models import Sum
from django.utils import timezone

from django.db import models
from django.db import transaction

from general_ledger.managers.transaction import TransactionQuerySet
from general_ledger.models import Direction
from general_ledger.models.mixins import UuidMixin


class Transaction(
    UuidMixin,
):

    logger = logging.getLogger("TransactionModel")
    objects = TransactionQuerySet.as_manager()

    # some put the description in the entry model. see xero, sage.
    # some put it in the transaction model. see modern treasury.
    description = models.CharField(max_length=200)
    # splits = models.ForeignKey(Split, on_delete=models.CASCADE)

    ledger = models.ForeignKey(
        "Ledger",
        on_delete=models.CASCADE,
    )

    """
    this is the date at which this transaction was posted to the ledger
    """
    post_date = models.DateTimeField(
        "post_date",
        null=True,
        blank=True,
    )

    """
    This is the date from the bank statement, or the date that was entered into the invoice etc
    """
    trans_date = models.DateField(
        "trans_date",
        null=True,
        blank=True,
    )

    trans_datetime = models.DateTimeField(
        "trans_date_time",
        null=True,
        blank=True,
    )

    is_posted = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # self.logger.debug(f"calling save in transaction: {self.description}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.post_date} {self.description}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        db_table = "gl_transaction"
        ordering = ["trans_date"]

    def get_entries(self, get_accounts: bool = False):
        if get_accounts:
            return self.entry_set.all().select_related("account")
        return self.entry_set.all()

    def get_debits(self):
        return self.entry_set.filter(tx_type="debit")

    @property
    def debit_amount(self):
        return (
            self.entry_set.filter(tx_type=Direction.DEBIT).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

    @property
    def credit_amount(self):
        return (
            self.entry_set.filter(tx_type=Direction.CREDIT).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

    def is_valid(self):
        """
        Check that the transaction is valid. This means that the sum of the debits and credits is zero.
        """
        return all(
            [
                self.is_balance_valid(),
            ]
        )

    def is_balance_valid(self):
        """
        Check that the transaction is valid. This means that the sum of the debits and credits is zero.
        """
        total = 0
        self.logger.debug(f"len(self.entry_set.all()): {len(self.entry_set.all())}")
        tot_credits = 0
        tot_debits = 0
        for entry in self.entry_set.all():
            self.logger.debug(
                f"total: {total} {entry.tx_type} {entry.account.type.direction}"
            )
            if entry.tx_type == Direction.CREDIT:
                tot_credits += entry.amount
            else:
                tot_debits += entry.amount
        self.logger.debug(f"tot_credits: {tot_credits} tot_debits: {tot_debits}")

        result = tot_credits == tot_debits

        return result

    def can_post(self):
        """
        Check if the transaction can be posted. This means that the transaction is valid and not already posted.
        """
        return all(
            [
                self.is_valid(),
                not self.is_posted,
            ]
        )

    def can_unpost(self):
        """
        Check if the transaction can be unposted. This means that the transaction is already posted and not in a locked state.
        """
        return all(
            [
                self.is_posted,
                not self.is_locked,
            ]
        )

    def can_delete(self):
        """
        Check if the transaction can be deleted. This means that the transaction is not already posted.
        """
        return all(
            [
                not self.is_posted,
            ]
        )

    @transaction.atomic
    def post(self):
        """
        Post the transaction.
        """
        if self.can_post():
            self.is_posted = True
            self.post_date = timezone.now()
            self.save()
            return True
        raise ValueError("Transaction cannot be posted")

    @transaction.atomic
    def unpost(self):
        """
        Unpost the transaction.
        """
        if self.can_unpost():
            self.is_posted = False
            self.save()
            return True
        raise ValueError("Transaction cannot be unposted")
