from django.db import models
from django.urls import reverse
import magic
import uuid


def generate_unique_filename(instance, filename):
    splitted = filename.split(".")
    if len(splitted) > 1:
        ext = splitted[-1]
        unique_filename = f"{uuid.uuid4()}.{ext}"
    else:
        ext = ""
        unique_filename = f"{uuid.uuid4()}"

    return "uploads/" + unique_filename


class FileUpload(models.Model):
    file = models.FileField(upload_to=generate_unique_filename)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    uploaded_name = models.CharField(max_length=100, null=True, blank=True)
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)

    sha256 = models.CharField(max_length=64, null=True, blank=True)

    def get_absolute_url(self):  # new
        return reverse("general_ledger:file-upload-detail", args=[str(self.pk)])

    def save(self, *args, **kwargs):

        if not self.name:
            self.name = self.file.name

        if self.file and not self.original_file_name:
            self.original_file_name = self.file.name

        if self.file:
            # temp_file_path = self.file.file.temporary_file_path()
            # print(f"Temporary file path: {temp_file_path}")
            # self.sha256 = hashlib.sha256(open(temp_file_path, "rb").read()).hexdigest()
            self.file.seek(0)
            first_2048_bytes = self.file.read(2048)
            # print(
            #     f"First 2048 bytes: {first_2048_bytes[:100]}..."
            # )
            filetype = magic.from_buffer(first_2048_bytes, mime=True)
            # print(f"Filetype: {filetype}")
            self.file_type = filetype
            self.file.seek(0)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name
