from django import forms

from general_ledger.models import FileUpload


class MultipleClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FileUploadForm(forms.Form):
    class Meta:
        # model = FileUpload
        fields = ["name", "file"]
        # exclude = ["book"]
        # widgets = {
        #     "file": MultipleClearableFileInput(
        #         attrs={"multiple": True},
        #     ),
        # }
    file = MultipleFileField()