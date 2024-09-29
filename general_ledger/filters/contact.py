import django_filters

from general_ledger.models import Contact


class ContactFilter(
    django_filters.FilterSet,
):
    is_supplier = django_filters.BooleanFilter()
    is_customer = django_filters.BooleanFilter()

    class Meta:
        model = Contact
        fields = [
            "is_supplier",
            "is_customer",
        ]

    # def filter_boolean(self, queryset, name, value):
    #     print(f"Filtering {name} with value: {value}")
    #     if value is not None:
    #         return queryset.filter(**{name: value})
    #     return queryset
    #
    # def filter_queryset(self, queryset):
    #     print(f"Raw data: {self.data}")
    #     print(f"Form data: {self.form.data}")
    #     print(f"Cleaned data: {self.form.cleaned_data}")
    #     for name, value in self.form.cleaned_data.items():
    #         queryset = self.filters[name].filter(queryset, value)
    #         print(f"After filtering by {name}: {queryset.query}")
    #     return queryset
