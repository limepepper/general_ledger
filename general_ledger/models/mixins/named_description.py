from django.db import models

import logging


class NameDescriptionMixin(models.Model):
    """
    An abstract base class model that provides name and description fields.
    """

    logger = logging.getLogger("NameDescriptionMixin")

    class Meta:
        abstract = True

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = slugify(self.name)[:20]
        # self.logger.debug("NameDescriptionMixin.save()")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
