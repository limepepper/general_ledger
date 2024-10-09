from django import forms
from django.contrib import admin

from general_ledger.models.file_upload import FileUpload
from general_ledger.utils import update_items


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "file",
        "uploaded_at",
    )
    actions = [
        update_items,
    ]
    class Meta:
        model = FileUpload
        fields = "__all__"
