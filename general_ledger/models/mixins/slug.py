from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify


def validate_slugify(value):
    if slugify(value) != value:
        raise ValidationError("Failed to validate slugify")


def slugify_unique(
    value,
    model,
    slugfield="slug",
    max_length=40,
):
    suffix = 0
    potential = base = slugify(value)[: (max_length - 2)]
    while True:
        if suffix > 100:
            raise ValueError("Too many potential slugs")
        if suffix:
            # print(f"suffixed: {suffix}")
            potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
            return potential
        suffix += 1


"""
https://stackoverflow.com/a/1490624/329931
above function is not my code, but i don't remember exactly where it comes from
you can find many snippets with such solutions searching for 'unique slug' and so
"""


class SlugMixin(models.Model):
    """
    An abstract base class model that provides a slug field.
    """

    class Meta:
        abstract = True

    slug = models.SlugField(
        max_length=22,
        blank=True,
        null=True,
        # validators=[validate_slugify],
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(
                self.name,
                self.__class__,
                max_length=24,
            )
            # self.slug = slugify(self.name)[:22]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug
