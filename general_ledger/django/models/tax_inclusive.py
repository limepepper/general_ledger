from django.db import models
from django.utils.translation import gettext_lazy as _


class TaxInclusive(models.TextChoices):
    INCLUSIVE = "Inc", _("Inclusive")
    EXCLUSIVE = "Exc", _("Exclusive")
    NONE = "Non", _("None")
