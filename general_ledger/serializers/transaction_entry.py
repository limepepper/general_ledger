from rest_framework import serializers

from general_ledger.models import Entry


class TransactionEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entry
        # fields = "__all__"
        fields = [
            "description",
            "account",
            "amount",
            "tx_type",
            "trans_date",
            "running_balance",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Entry.objects.create(**validated_data)
