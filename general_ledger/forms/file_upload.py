from django.forms import ModelForm

from general_ledger.models import FileUpload


class FileUploadForm(ModelForm):
    class Meta:
        model = FileUpload
        fields = ["name", "file"]
        # exclude = ["book"]
