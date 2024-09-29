from django.db import models

import logging


class CreatedUpdatedMixin(models.Model):
    """
    An abstract base class model that provides created_at and updated_at fields.
    """

    logger = logging.getLogger("CreatedUpdatedMixin")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = slugify(self.name)[:20]
        # self.logger.debug("CreatedUpdatedMixin.save()")

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"c:{self.created_at} u:{self.updated_at}"
