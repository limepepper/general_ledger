from decimal import Decimal

from django.db import connection
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import generics
from rest_framework.response import Response
from rich import inspect

from general_ledger.filters.bank_transaction import BankStatementFilter
from general_ledger.models import BankStatementLine
from general_ledger.serializers.bank_transaction import BankStatementGroupedSerializer
from datetime import datetime, timedelta


class BankStatementGroupedView(generics.ListAPIView):
    queryset = BankStatementLine.objects.all()
    serializer_class = BankStatementGroupedSerializer
    filterset_class = BankStatementFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        if connection.vendor == "sqlite":
            queryset = queryset.extra(select={"date_only": "date(date)"})
        else:
            queryset = queryset.annotate(date_only=TruncDate("date"))

        return (
            queryset.values("date_only")
            .annotate(total_amount=Sum("amount"))
            .order_by("date_only")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        print(f"Queryset: {queryset}")

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Create a dictionary of existing data
            #            data_dict = {item["date_only"]: item["total_amount"] for item in queryset}
            data_dict = {
                (
                    item["date_only"].strftime("%Y-%m-%d")
                    if isinstance(item["date_only"], datetime)
                    else item["date_only"]
                ): item["total_amount"]
                for item in queryset
            }

            # inspect(data_dict, methods=False)

            # Generate a complete date range and fill in missing dates with zero
            complete_data = []
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                amount = data_dict.get(date_str, Decimal("0"))
                # inspect(f"{current_date=}, {amount=}")
                # print(f"{current_date=}, {amount=}")
                complete_data.append({"date": date_str, "amount": amount})
                current_date += timedelta(days=1)

            # inspect(complete_data, methods=False)

            serializer = self.get_serializer(complete_data, many=True)
        else:
            print(f"not filtered")
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
