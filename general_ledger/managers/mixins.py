from django.db import models


class CommonAggregationMixins(models.QuerySet):

    field = None

    def sum(self, field):
        return self.aggregate(models.Sum(field))[f"{field}__sum"]

    def avg(self, field):
        return self.aggregate(models.Avg(field))[f"{field}__avg"]

    def between(self, field, start_date, end_date, **filters,):
        qs = self.filter(**filters)

        if start_date:
            qs = qs.filter(**{f"{field}__gte": start_date})

        if end_date:
            qs = qs.filter(**{f"{field}__lte": end_date})

        return qs

    def sum_between(
        self,
        field,
        start_date,
        end_date,
        **filters,
    ):
        qs = self.filter(**filters)

        if start_date:
            qs = qs.filter(date__gte=start_date)

        if end_date:
            qs = qs.filter(date__lte=end_date)

        return qs.sum(field)
