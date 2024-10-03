from django.db import models


class BankStatementLineManager(models.Manager):

    def for_bank(self, bank):
        return self.get_queryset().filter(
            bank=bank,
            is_active=True,
        )
