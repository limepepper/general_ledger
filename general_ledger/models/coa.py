import logging

from django.db import models

from general_ledger.models.mixins import NameDescriptionMixin, UuidMixin, SlugMixin


class ChartOfAccountsManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "book",
        )

    def for_book(self, book):
        return self.get_queryset().filter(
            book=book,
        )


class ChartOfAccounts(
    UuidMixin,
    NameDescriptionMixin,
    SlugMixin,
):

    logger = logging.getLogger(__name__)
    objects = ChartOfAccountsManager()

    class Meta:
        verbose_name = "Chart of Accounts"
        verbose_name_plural = "Charts of Accounts"
        db_table = "gl_coa"
        ordering = ["name"]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
    )

    is_system = models.BooleanField(default=False)
    is_placeholder = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        if self.book_id:
            return f"{self.name} {self.book}"
        return f"{self.name}"

    def get_sales_account(self):
        return self.account_set.get(
            name="Sales",
        )

    def get_sales_tax_rate(self):
        return self.account_set.get(
            name="Sales",
        )
