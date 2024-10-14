from collections import defaultdict
from decimal import Decimal

from django.db import models
from django.db.models import Case, When, IntegerField
from django.db.models import F, Func, Value, CharField
from django.db.models.functions import TruncYear, TruncMonth, TruncWeek, TruncDay
from loguru import logger
from rich import inspect
from django.db.models import CharField
from django.db.models.functions import Cast
from general_ledger.managers.mixins import CommonAggregationMixins
from general_ledger.models import Direction


class EntryQuerySet(
    CommonAggregationMixins,
):
    date_field = "transaction__trans_date"

    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.debit_bd = Decimal("0.00")
        self.credit_bd = Decimal("0.00")

    def set_balances_bd(self, debit_bd=None, credit_bd=None):
        if debit_bd:
            self.debit_bd = debit_bd
        if credit_bd:
            self.credit_bd = credit_bd
        return self

    def debits(self):
        return self.filter(tx_type=Direction.DEBIT)

    def credits(self):
        return self.filter(tx_type=Direction.CREDIT)

    def debit_balance(self):
        """
        this is the total from the perspective of the debit side
        i.e. if the account is a debit account, this is the total
        by which the debits exceed the credits. If you want the sum of
        all the debits, the debit_total() method is what you want.
        :return:
        """
        return self.debit_total() - self.credit_total()

    def debit_total(self):
        total = sum([entry.amount for entry in self.filter(tx_type=Direction.DEBIT)])
        total += self.debit_bd
        return total if total else Decimal("0.00")

    def credit_balance(self):
        return self.credit_total() - self.debit_total()

    def credit_total(self):
        total = sum([entry.amount for entry in self.filter(tx_type=Direction.CREDIT)])
        total += self.credit_bd
        return total if total else Decimal("0.00")

    def is_credit_balance(self):
        return self.credit_total() > self.debit_total()

    def is_debit_balance(self):
        return self.debit_total() > self.credit_total()

    def is_empty(self):
        return not any(
            [
                self.debit_bd,
                self.credit_bd,
                self.count(),
            ]
        )

    def is_balanced(
        self,
    ):
        """
        is the entry set balanced? optionally correct for any balance brought down
        :param debit_bd:
        :param credit_bd:
        :return:
        """
        return self.debit_total() == self.credit_total()

    def annotate_by_interval(self, interval):
        if interval == "year":
            return self.annotate(interval_key=TruncYear(self.date_field))
        elif interval == "month":
            return self.annotate(interval_key=TruncMonth(self.date_field))
        elif interval == "week":
            return self.annotate(interval_key=TruncWeek(self.date_field))
        elif interval == "day":
            return self.annotate(interval_key=TruncDay(self.date_field))
        else:
            raise ValueError("Invalid interval")

    def annotate_by_financial_year(self, start_month=4):
        return self.annotate(
            interval_key=Case(
                When(date__month__gte=start_month, then=F("date__year")),
                When(date__month__lt=start_month, then=F("date__year") - 1),
                output_field=IntegerField(),
            )
        )

    def get_grouped_entries(self, interval):
        if "interval_key" in self.query.annotations:
            logger.debug("Already annotated with interval_key")
        else:
            logger.debug("No interval annotation found")

        entry_set = self.annotate_by_interval(interval)
        entry_set = entry_set.annotate(
            interval_key_str=Cast("interval_key", CharField())
        )

        grouped_entries = defaultdict(dict)

        interval_keys = (
            entry_set.values_list("interval_key_str", flat=True)
            .distinct()
            .order_by("interval_key_str")
        )
        # preserve the dt field, so we don't have to cast back again
        interval_keys_dt = (
            entry_set.values_list("interval_key", flat=True)
            .distinct()
            .order_by("interval_key")
        )

        # inspect(interval_keys)
        # inspect(interval_keys_dt)

        grouped_entries["meta"]["interval_keys"] = interval_keys

        for i, interval_key in enumerate(interval_keys):
            grouped_entries[interval_key]["entries"] = entry_set.filter(
                interval_key_str=interval_key
            )
            grouped_entries[interval_key]["interval_key_dt"] = interval_keys_dt[i]
            grouped_entries[interval_key]["interval_key"] = interval_keys[i]

        return grouped_entries

    def __rich_repr__(self):
        yield "Transaction", {}
        yield "Count", self.count()
        yield "Entries", str(self)
        yield


class EntryManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "account",
                "transaction",
            )
        )
