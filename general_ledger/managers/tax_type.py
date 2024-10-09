from django.db import models


class TaxTypeManager(models.Manager):

    def get_by_natural_key(self, slug, book):
        return self.get(slug=slug, book=book)
