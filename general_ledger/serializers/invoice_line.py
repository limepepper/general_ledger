from rest_framework import serializers

from general_ledger.models import InvoiceLine


class InvoiceLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceLine
        # fields = "__all__"
        fields = [
            "id",
            "name",
            "quantity",
            "unit_price",
            "account",
            "vat_rate",
            "order",
            "line_total_inclusive",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return InvoiceLine.objects.create(**validated_data)
