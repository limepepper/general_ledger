from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from rest_framework import permissions

from dynamic_preferences.api import viewsets
from django.db import models

from dashboard.models import BookPreferenceModel
from general_ledger.django.models import Book


# class UserPreferencesViewSet(viewsets.PerInstancePreferenceViewSet):
#     queryset = models.UserPreferenceModel.objects.all()
#     serializer_class = serializers.UserPreferenceSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_related_instance(self):
#         return self.request.user


class BookPreferenceViewSet(viewsets.PerInstancePreferenceViewSet):
    queryset = BookPreferenceModel.objects.all()

    #
    # # def get_queryset(self):
    # #     return (
    # #         super(PerInstancePreferenceViewSet, self)
    # #         .get_queryset()
    # #         .filter(instance=self.get_related_instance())
    # #     )
    # #
    # # def get_related_instance(self):
    # #     return self.request.user
    #
    def get_related_instance(self):
        """Override this to the instance bound to the preferences"""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        print(f"lookup_url_kwarg: {lookup_url_kwarg}")
        Book.objects.get(pk=self.kwargs[lookup_url_kwarg])
