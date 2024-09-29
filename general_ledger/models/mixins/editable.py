from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive


class EditableMixin(models.Model):
    """
    method to check if the object is editable
    """

    class Meta:
        abstract = True

    def can_edit(self):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        if not self.can_edit():
            raise ValidationError("Cannot delete when can edit is false.")
        super().delete(*args, **kwargs)
