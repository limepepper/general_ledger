from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import FieldFile


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (UploadedFile, FieldFile)):
            return o.name
        if isinstance(o, Model):
            return repr(o)
        if hasattr(o, "__iter__"):
            return [self.default(i) for i in o]
        return super().default(o)
