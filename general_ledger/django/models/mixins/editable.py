from django.core.exceptions import ValidationError
from django.db import models


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
