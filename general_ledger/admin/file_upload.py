from django import forms
from django.contrib import admin

from general_ledger.models.file_upload import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "file",
        "uploaded_at",
    )

    class Meta:
        model = FileUpload
        fields = "__all__"
