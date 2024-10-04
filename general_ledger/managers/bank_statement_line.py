from django.db import models

from general_ledger.managers.mixins import CommonAggregationMixins


class BankStatementLineManagerQuerySet(CommonAggregationMixins,models.QuerySet,):

    def for_bank(self, bank):
        return self.filter(
            bank=bank,
            is_active=True,
        )


class BankStatementLineManager(models.Manager):

    def for_bank(self, bank):
        return self.get_queryset().filter(
            bank=bank,
            is_active=True,
        )
