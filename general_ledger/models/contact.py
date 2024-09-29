import logging

from django.db import models

from general_ledger.managers.contact import ContactManager, ContactQuerySet
from general_ledger.models.mixins import LinksMixin
from general_ledger.models.mixins import UuidMixin, CreatedUpdatedMixin
from general_ledger.models.tax_inclusive import TaxInclusive


class Contact(
    UuidMixin,
    CreatedUpdatedMixin,
    LinksMixin,
):
    """
    The `Contact` class represents a contact entity in the general ledger system.
    {@see UuidMixin}
    {@see general_ledger.admin.contact.ContactAdmin:test}
    [general_ledger/admin/contact.py]

    Attributes:
        book (models.ForeignKey): Foreign key to the Book model.
        name (models.CharField): Name of the contact.
        address (models.CharField): Address of the contact.
        phone (models.CharField): Phone number of the contact.
        email (models.EmailField): Email address of the contact.
        company_number (models.CharField): Company number of the contact.
        is_customer (models.BooleanField): Indicates if the contact is a customer.
        is_supplier (models.BooleanField): Indicates if the contact is a supplier.
        is_demo (models.BooleanField): Indicates if the contact is a demo contact.
        is_vat_registered (models.BooleanField): Indicates if the contact is VAT registered.
        vat_number (models.CharField): VAT number of the contact.
        sales_account (models.ForeignKey): Foreign key to the sales account.
        sales_tax_rate (models.ForeignKey): Foreign key to the sales tax rate.
        sales_tax_inclusive (models.CharField): Indicates if sales tax is inclusive.
        purchases_account (models.ForeignKey): Foreign key to the purchases account.
        purchases_tax_rate (models.ForeignKey): Foreign key to the purchases tax rate.
        purchases_tax_inclusive (models.CharField): Indicates if purchases tax is inclusive.

    Methods:
        natural_key(): Returns the natural key for the contact.
        save(*args, **kwargs): Custom save method for the contact.
        __str__(): Returns the string representation of the contact.
    """

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    objects = ContactManager.from_queryset(ContactQuerySet)()

    class Meta:
        verbose_name_plural = "Contacts"
        db_table = "gl_contact"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "book"], name="name_book_uniq")
        ]

    def natural_key(self):
        return self.name, self.book

    # generic view class attributes
    links_detail = "general_ledger:contact-detail"
    links_list = "general_ledger:contact-list"
    links_create = "general_ledger:contact-create"
    links_edit = "general_ledger:contact-update"
    links_title_field = "name"

    generic_list_display = (
        "name",
        "email",
        "is_customer",
        "is_supplier",
    )

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=100)
    address = models.CharField(
        max_length=100,
        blank=True,
    )
    phone = models.CharField(
        max_length=100,
        blank=True,
    )
    email = models.EmailField(
        blank=True,
    )
    company_number = models.CharField(max_length=12, blank=True, null=True)

    is_customer = models.BooleanField(default=True)
    is_supplier = models.BooleanField(default=False)

    is_demo = models.BooleanField(default=False)
    is_vat_registered = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=12, blank=True, null=True)

    sales_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="sales_contacts",
        null=True,
        blank=True,
    )

    sales_tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
        related_name="sales_tax_contacts",
        null=True,
        blank=True,
    )

    sales_tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    purchases_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="purchases_contacts",
        null=True,
        blank=True,
    )

    purchases_tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.CASCADE,
        related_name="purchases_tax_contacts",
        null=True,
        blank=True,
    )

    purchases_tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    #
    ## Do custom handling stuff upon saving an contact
    #
    def save(self, *args, **kwargs):
        self.logger.debug(f"saving contact: {self}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
