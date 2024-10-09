import logging

from django.db import models

from .mixins import (
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
)
from ..managers.tax_type import TaxTypeManager


class TaxType(
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
):
    """
    It is probably the case the tax type needs some logic
    associated with it. For example, some sort of calcualted based
    on region or type of product.
    """

    logger = logging.getLogger(__name__)

    objects = TaxTypeManager()

    class Meta:
        verbose_name = "Tax Type"
        verbose_name_plural = "Tax Type"
        db_table = "gl_tax_type"
        unique_together = [
            ["slug", "book"],
            ["name", "book"],
        ]

    def natural_key(self):
        return self.slug, self.book

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=50,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_visible = models.BooleanField(
        default=True,
    )

    is_deprecated = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name
