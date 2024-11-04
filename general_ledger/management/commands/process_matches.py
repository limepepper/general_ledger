from loguru import logger

from django.core.management.base import BaseCommand
from rich import inspect

from general_ledger.helpers.matcher import MatcherHelper


class Command(BaseCommand):
    help = "generate sample banks"

    def handle(self, *args, **kwargs):
        logger.info("Processing matches")
        matcher = MatcherHelper()
        matcher.reconcile_bank_statement()

        for candidate in matcher.candidates["exact"]:
            logger.info(candidate)
            bank_transaction, invoices = candidate
            matcher.reconcile(bank_transaction, invoices)
