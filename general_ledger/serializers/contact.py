from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact


# Serializers define the API representation.
class ContactSerializer(serializers.HyperlinkedModelSerializer):
    # book = serializers.HyperlinkedIdentityField(
    #     view_name="general_ledger:book-detail", format="html"
    # )

    class Meta:
        model = Contact
        # fields = "__all__"
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "book",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Contact.objects.create(**validated_data)
