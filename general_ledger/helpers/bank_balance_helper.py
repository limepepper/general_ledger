# import logging
import datetime
from datetime import date
from datetime import timedelta
from decimal import Decimal

from django.db import models
from loguru import logger
from rich import inspect

from general_ledger.models import BankBalance


def inspects(qs):
    pass


class BankBalanceHelper:
    def __init__(self, bank_account):
        logger.trace(f"BankBalanceHelper: {bank_account}")
        self.bank_account = bank_account

    def get_balance(
        self,
        start_date=None,
        end_date=date.today() - timedelta(days=1),
        type_filter=None,
    ):

        qs = self.bank_account.bankstatementline_set.all()

        if start_date:
            qs = qs.filter(date__gte=start_date)

        if end_date:
            qs = qs.filter(date__lte=end_date)

        dts = qs.dates("date", "day")

        # inspect(qs)
        # inspect(dts)

        balances = []
        for dt in dts:
            sls_qs = qs.filter(date__lte=dt)
            balance_on_date = sls_qs.filter(date__lte=dt).aggregate(
                models.Sum("amount")
            )["amount__sum"]
            example = sls_qs.last()
            if example:
                tz = example.tz
            else:
                tz = self.bank_account.tz

            balances.append(
                (
                    dt,
                    balance_on_date if balance_on_date is not None else Decimal(0),
                    tz,
                )
            )

        for balance in balances:
            print(f"{balance[0]} {balance[1]}")
            bal, created = BankBalance.objects.update_or_create(
                balance_date=datetime.datetime(
                    balance[0].year,
                    balance[0].month,
                    balance[0].day,
                    tzinfo=balance[2],
                ),
                bank=self.bank_account,
                balance_type="ephemeral",
                defaults={
                    "balance": balance[1],
                    "balance_source": "factory",
                },
            )
            print(f"{bal.balance_date} {bal.balance} {created}")

        for balance in balances:
            print(f"{balance[0]} {balance[1]}")
            bal, created = BankBalance.objects.update_or_create(
                balance_date=datetime.datetime(
                    balance[0].year,
                    balance[0].month,
                    balance[0].day,
                    tzinfo=balance[2],
                ),
                bank=self.bank_account,
                balance_type="ephemeral",
                defaults={
                    "balance": balance[1],
                    "balance_source": "factory",
                },
            )
            print(f"{bal.balance_date} {bal.balance} {created}")


#        return self.bank_account.balance
