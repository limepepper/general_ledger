from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive


# this is a bunch of app specific mixins


class ValidatableModelMixin(models.Model):
    """
    Mixin that sets a validation property
    allow recursive validation
    """

    class Meta:
        abstract = True

    @property
    def is_valid(self):
        return self.validate()

    def validate(self):
        try:
            self.full_clean(),
            return True
        except ValidationError as e:
            logger.error(f"Model <{self._meta.model_name}> validation failed {e}")
            return False
