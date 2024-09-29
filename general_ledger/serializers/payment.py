from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Payment


# Serializers define the API representation.
class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        # fields = [
        #     "name",
        #     "amount",
        #     "date",
        #     "state",
        # ]

    def create(self, validated_data):
        """
        Create and return a new `Payment` instance, given the validated data.
        """
        return Payment.objects.create(**validated_data)
