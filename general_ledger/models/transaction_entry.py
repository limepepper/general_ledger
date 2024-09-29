import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from general_ledger.models.mixins import CreatedUpdatedMixin
from .direction import Direction


class Entry(
    CreatedUpdatedMixin,
):

    logger = logging.getLogger(__name__)

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Transaction Entries"
        db_table = "gl_transaction_entry"

        ordering = ["transaction__trans_date"]

    # some put the description in the entry model. see xero, sage.
    # some put it in the transaction model. see modern treasury.
    description = models.CharField(
        max_length=200,
    )

    account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
    )

    transaction = models.ForeignKey(
        "Transaction",
        on_delete=models.CASCADE,
    )

    amount = models.DecimalField(
        decimal_places=4,
        max_digits=20,
        default=0.00,
        verbose_name=_("Amount"),
        help_text=_("Account of the transaction."),
        validators=[MinValueValidator(0)],
    )

    tx_type = models.CharField(
        max_length=10,
        choices=Direction.choices,
        default=Direction.DEBIT,
        verbose_name=_("Tx Type"),
    )

    @property
    def tx_type_enum(self):
        return Direction(self.tx_type)

    @property
    def is_debit(self):
        return self.tx_type_enum == Direction.DEBIT

    @property
    def is_credit(self):
        return self.tx_type_enum == Direction.CREDIT

    @property
    def trans_date(self):
        return self.transaction.trans_date

    def running_balance(self):
        running_balance = 0
        for entry in self.account.entry_set.order_by("transaction__trans_date"):
            # print(f"entry: {entry}")
            if entry.tx_type == self.account.type.direction:
                # print(f"returning +ve {entry.amount}")
                running_balance += entry.amount
            else:
                # print(f"returning -ve {entry.amount}")
                running_balance -= entry.amount

            if entry == self:
                return running_balance
        raise ValueError("Entry not found in account")

    def save(self, *args, **kwargs):
        self.logger.info(f"calling save in entry: {self.amount} {self.tx_type}")

        super().save(*args, **kwargs)

    def get_counter_entry(self):
        """
        if the entry has a single opposite, return it
        """
        counter_entry = self.transaction.entry_set.filter(
            ~Q(id=self.id) & Q(tx_type=Direction(self.tx_type).opposite())
        )
        # .annotate(
        #     accounts=StringAgg(Cast("account__name", CharField()), delimiter=",")
        # )
        # .values("accounts")
        # )
        names = ", ".join([item.account.name for item in counter_entry])
        return names

    def __str__(self):
        try:
            account_name = self.account.name
        except ObjectDoesNotExist:
            account_name = "None"
        try:
            tx_type = self.tx_type
        except ObjectDoesNotExist:
            tx_type = "None"

        return f"{account_name} {type(tx_type)} {self.amount}"
