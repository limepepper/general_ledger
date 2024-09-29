import logging

from django_select2 import forms as s2forms


class ContactWidget(s2forms.ModelSelect2Widget):

    logger = logging.getLogger(__name__)

    search_fields = [
        "name__icontains",
    ]

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        if request.user.is_authenticated:
            return (
                super()
                .filter_queryset(request, term, queryset, **dependent_fields)
                .filter(book=request.active_book)
            )
        return self.queryset.none()
