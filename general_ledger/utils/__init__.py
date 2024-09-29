from django.contrib import admin

from .json_encoder import JSONEncoder
from .pretty_yaml import PrettyYAML


@admin.action(description="resave items to force recalculation")
def update_items(modeladmin, request, queryset):
    """
    if the model has changed, then re-save to force recalculations on save

    """
    for obj in queryset:
        obj.save()
