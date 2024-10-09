from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from pandas.core.dtypes.inference import is_integer

from general_ledger.forms_widgets.file_upload import MultipleFileField

# Add to your settings file
CONTENT_TYPES = [
    "image",
    "video",
    "text",
    "application",
]
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_SIZE = 5242880


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

    def clean_file(self):

        contents = self.cleaned_data["file"]
        if isinstance(contents, (list, tuple)):
            for content in contents:
                content_type = content.content_type.split("/")[0]
                if content_type in CONTENT_TYPES:
                    if content.size > int(MAX_UPLOAD_SIZE):
                        raise forms.ValidationError(
                            _("Please keep filesize under %s. Current filesize %s")
                            % (
                                filesizeformat(MAX_UPLOAD_SIZE),
                                filesizeformat(content.size),
                            )
                        )
                else:
                    raise forms.ValidationError(_(f"fFile type '{content_type}' is not supported"))
                return content
