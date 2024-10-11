import logging

from django.db.models import Sum
from django.utils import timezone

from django.db import models
from django.db import transaction

from general_ledger.models import Direction
from general_ledger.models.mixins import UuidMixin


class TransactionQuerySet(models.QuerySet):
    def posted(self):
        return self.filter(is_posted=True)

    def unposted(self):
        return self.filter(is_posted=False)

    def locked(self):
        return self.filter(is_locked=True)

    def unlocked(self):
        return self.filter(is_locked=False)
