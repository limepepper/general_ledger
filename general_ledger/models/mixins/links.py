from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from loguru import logger

from general_ledger.models.tax_inclusive import TaxInclusive


class LinksMixin(models.Model):
    """
    Mixin that sets a link property
    """

    class Meta:
        abstract = True

    @property
    def edit_link(self):
        return format_html(
            '<a href="{}">{}</a>',
            self.get_edit_url(),
            getattr(self, self.links_title_field),
        )

    def get_edit_url(self):
        return reverse(self.links_edit, args=[str(self.pk)])

    @property
    def link(self):
        return """<a href="{0}">{1}</a>""".format(
            self.get_absolute_url(), getattr(self, self.links_title_field)
        )

    def get_absolute_url(self):  # new
        return reverse(self.links_detail, args=[str(self.pk)])

    def get_delete_url(self):
        return reverse(self.links_edit, args=[str(self.pk)])

    @property
    def admin_link(self):
        return format_html(
            '<a href="{}">{}</a>',
            self.get_admin_url(),
            self.name,
        )

    def get_admin_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[str(self.pk)],
        )
