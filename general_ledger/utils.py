from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import FieldFile


@admin.action(description="resave items to force recalculation")
def update_items(modeladmin, request, queryset):
    """
    if the model has changed, then re-save to force recalculations on save

    """
    for obj in queryset:
        obj.save()


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (UploadedFile, FieldFile)):
            return o.name
        if isinstance(o, Model):
            return repr(o)
        if hasattr(o, "__iter__"):
            return [self.default(i) for i in o]
        return super().default(o)
