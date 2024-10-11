from django.contrib import admin


class DjangoUtil:
    @staticmethod
    def get_fields(model):
        """find a subset of fields for display in a table or UI"""
        fields = [getattr(field, "name") for field in model._meta.fields]
        if hasattr(model, "generic_list_display"):
            return [x for x in fields if x in model.generic_list_display]
        elif hasattr(model, "list_display"):
            return [x for x in fields if x in model.list_display]
        else:
            try:
                modeladmin = admin.site._registry[model]
                if modeladmin:
                    return [x for x in fields if x in modeladmin.list_display]
            except KeyError:
                pass
        return [getattr(field, "name") for field in model._meta.fields]
