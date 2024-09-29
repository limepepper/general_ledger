import logging

from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse

from general_ledger.helpers.book import BookHelper
from general_ledger.managers.book import BookManager, BookQuerySet
from general_ledger.models.mixins import (
    BusinessAccountsMixin,
    DocumentSequencePrefixMixin,
)
from general_ledger.models.permissions import UserBookAccess
from general_ledger.models.mixins import (
    CreatedUpdatedMixin,
    UuidMixin,
    SlugMixin,
)
from django.contrib.auth import get_user_model


class Book(
    UuidMixin,
    CreatedUpdatedMixin,
    SlugMixin,
    BusinessAccountsMixin,
    DocumentSequencePrefixMixin,
):
    """
    A book is a collection of ledgers. It is the top level of the general ledger. In the real world it is the entity
    that contains all the ledgers for a company. This could also be
    a person's personal book. It is the top level of the general ledger.
    """

    logger = logging.getLogger(__name__)

    objects = BookManager.from_queryset(queryset_class=BookQuerySet)()

    class Meta:
        verbose_name_plural = "books"
        db_table = "gl_book"
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "slug"],
                name="book_uniq_owner_slug",
            )
        ]

    def natural_key(self):
        return (self.slug,) + self.owner.natural_key()

    # natural_key.dependencies = ["auth.User"]

    # root_account = models.CharField(max_length=200)
    name = models.CharField(
        max_length=70,
        unique=True,
        verbose_name="Book Name",
        blank=False,
        null=False,
        validators=[MinLengthValidator(3)],
        help_text="The name must be at least 3 characters long.",
    )

    ## Relationships @TODO: this is pretty simplistic
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    users = models.ManyToManyField(
        get_user_model(),
        through="UserBookAccess",
        related_name="accessible_books",
    )

    # not using this. but was intended to be used for the demo
    # account and limit things like file uploads
    is_demo = models.BooleanField(default=False)
    is_vat_registered = models.BooleanField(default=False)

    business_name = models.CharField(max_length=100, blank=True, null=True)
    business_address = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=12, blank=True, null=True)
    company_number = models.CharField(max_length=12, blank=True, null=True)
    business_website = models.URLField(blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)

    def user_has_access(self, user):
        return (
            self.is_demo or self.owner == user or self.users.filter(id=user.id).exists()
        )

    def give_access_to_user(self, user, read_only=False):
        if not self.user_has_access(user):
            UserBookAccess.objects.create(
                user=user, entity=self, is_read_only=read_only
            )

    def remove_user_access(self, user):
        if user != self.owner:
            UserBookAccess.objects.filter(user=user, entity=self).delete()

    @property
    def link(self):
        return """<a href="{0}">{1}</a>""".format(self.get_absolute_url(), self.name)

    def get_absolute_url(self):  # new
        return reverse("general_ledger:book-detail", args=[str(self.pk)])

    # this is only here bcause the validator doesn't run on
    # code saves. It only runs on form saves.
    # @TODO remove this?
    def save(self, *args, **kwargs):
        self.logger.info(f"calling save in book: {self.name}")
        # this cause save to fail. but commented out for now
        self.full_clean()  # This will call the clean method
        super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=["invoice_sequence"])

    def __str__(self):
        return self.name

    # @TODO: this is not robust for future use
    def get_default_ledger(self):
        return self.ledger_set.first()

    # @TODO: this is not robust for future use
    def get_default_coa(self):
        return self.chartofaccounts_set.first()

    def is_initialized(self):
        ledger = self.get_default_ledger()
        coa = self.get_default_coa()
        sales_account = coa.account_set.get(name="Sales")
        return ledger and coa

    def initialize(self):
        helper = BookHelper(book=self)
        helper.init_data()
