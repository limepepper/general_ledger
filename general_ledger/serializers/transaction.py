from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Transaction
from general_ledger.serializers.transaction_entry import TransactionEntrySerializer


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    entry_set = TransactionEntrySerializer(many=True, read_only=False)

    class Meta:
        model = Transaction
        # fields = "__all__"
        fields = [
            "id",
            "trans_date",
            "post_date",
            "is_posted",
            "description",
            "debit_amount",
            "credit_amount",
            "entry_set",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Transaction.objects.create(**validated_data)
