from django.db import models
from loguru import logger
from xstate_machine import FSMField, transition

from general_ledger.helpers.payment import PaymentHelper
from general_ledger.models.document_status import DocumentStatus
from general_ledger.models.mixins import (
    LinksMixin,
    ValidatableModelMixin,
    EditableMixin,
)
from general_ledger.models.mixins import UuidMixin, CreatedUpdatedMixin


class PaymentManager(models.Manager):
    pass
    # def get_queryset(self):
    #     return (
    #         super()
    #         .get_queryset()
    #         .select_related(
    #             "bank_statement_line",
    #             "invoice",
    #         )
    #     )
