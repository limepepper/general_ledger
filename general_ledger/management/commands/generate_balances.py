import uuid

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from loguru import logger
import pytz
from general_ledger.models import BankBalance


class Command(BaseCommand):
    help = "generate balances data"

    def handle(self, *args, **kwargs):
        logger.info("===========Generating Financial Data==========")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT date, bank_id, SUM(amount) OVER (PARTITION BY bank_id ORDER BY date) as running_balance
                FROM gl_bank_statement_line
                ORDER BY bank_id, date;
            """
            )

            rows = cursor.fetchall()

        for row in rows:
            date, bank_id, balance = row
            logger.info(f"Date: {date}, Bank ID: {bank_id}, Balance: {balance}")
            BankBalance.objects.create(
                balance_date=date,
                bank_id=bank_id,
                balance=balance,
                balance_source="calculated",
                created_at=timezone.now(),
                updated_at=timezone.now(),
                balance_type="ephemeral",
                id=uuid.uuid4(),
            )

        self.stdout.write(self.style.SUCCESS("Successfully inserted running balances"))
