from enum import Enum

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class DocumentStatus(models.TextChoices):
    DRAFT = "DR", "Draft"
    RECORDED = "RE", "Recorded"
    POSTED = "PO", "Posted"
    PARTIAL = "PA", "Partial"
    COMPLETE = "CO", "Complete"
    CANCELLED = "CA", "Cancelled"
    VOID = "VO", "Void"
