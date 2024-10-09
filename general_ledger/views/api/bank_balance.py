from rest_framework import viewsets
from rich import inspect

from general_ledger.models import BankBalance
from general_ledger.serializers.bank_balance import BankBalanceSerializer
from datetime import datetime, timedelta


class BankBalanceViewSet(
    viewsets.ModelViewSet,
):
    queryset = BankBalance.objects.all()
    serializer_class = BankBalanceSerializer
    pagination_class = None

    def get_queryset(self):
        bank_id = self.request.query_params.get("bank_id", None)
        if not bank_id:
            return BankBalance.objects.none()

        start_date = self.request.query_params.get(
            "start_date", (datetime.now() - timedelta(days=1080)).strftime("%Y-%m-%d")
        )
        end_date = self.request.query_params.get(
            "end_date", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        )
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        queryset = self.queryset.filter(
            balance_date__gte=start_date,
            balance_date__lte=end_date,
            bank__id=bank_id,
        )
        # inspect(queryset, methods=False)
        return queryset
