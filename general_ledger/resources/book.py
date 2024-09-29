import logging

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from general_ledger.models import Book
from django.contrib.auth import get_user_model


class BookResource(resources.ModelResource):

    logger = logging.getLogger(__name__)

    owner = fields.Field(
        column_name="owner",
        attribute="owner",
        widget=ForeignKeyWidget(get_user_model(), field="uuid"),
    )

    class Meta:
        model = Book
        # fields = "__all__"
        import_id_fields = ("uuid",)
        # exclude = ("tax_type",)
