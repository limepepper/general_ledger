from django.db import models
from django.template.defaultfilters import slugify
from uuid import uuid4

import logging


class UuidMixin(models.Model):
    """
    An abstract base class model that provides and creates a UUID field.
    """

    logger = logging.getLogger(__name__)

    class Meta:
        abstract = True

    id = models.UUIDField(
        default=uuid4,
        # @TODO any way to avoid this as it makes it show
        # up in the admin interface
        # editable=False,
        unique=True,
        primary_key=True,
    )
