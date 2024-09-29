import logging

from django.db import models

from general_ledger.managers.tax_rate import TaxRateManager
from general_ledger.models.mixins import (
    NameDescriptionMixin,
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)


class TaxRate(
    UuidMixin,
    NameDescriptionMixin,
    CreatedUpdatedMixin,
    SlugMixin,
):
    """
    This model represents a tax table. Is uk based at the moment
    """

    logger = logging.getLogger(__name__)
    objects = TaxRateManager()

    class Meta:
        verbose_name = "Tax Rate"
        verbose_name_plural = "Tax Rates"
        db_table = "gl_tax_rate"
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "tax_type"], name="slug_tax_type_uniq"
            ),
            models.UniqueConstraint(
                fields=["slug", "book"],
                name="tax_rate_uniq_slug_book",
            ),
            models.UniqueConstraint(
                fields=["name", "book"],
                name="tax_rate_uniq_name_book",
            ),
        ]

    def natural_key(self):
        return self.slug, self.book

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    tax_type = models.ForeignKey(
        "TaxType",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=70,
        blank=False,
        null=False,
    )

    # @TODO: customize how this field is titled in tables
    short_name = models.CharField(
        max_length=6,
        blank=False,
        null=False,
        verbose_name="Short Name",
    )

    # short_name.description = ("Short name for the tax rate",)

    # @TODO: capture the idea of composite tax rates. i.e. local tax + national tax
    rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=False,
        null=False,
        default=0.00,
    )

    is_visible = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    # "This is the default tax rate for the book for this tax type",
    is_default = models.BooleanField(
        default=False,
    )

    # if a tax is being introduced in the future. this is for coordination
    effective_date = models.DateField(
        null=True,
        blank=True,
    )

    # if a tax is being removed in the future. this is for coordination
    end_date = models.DateField(
        null=True,
        blank=True,
    )
