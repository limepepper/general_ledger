from django.db import models


class CommonBooleanMixins(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def posted(self):
        return self.filter(
            is_posted=True,
        )

    def unposted(self):
        return self.filter(
            is_posted=False,
        )

    def locked(self):
        return self.filter(
            is_locked=True,
        )

    def unlocked(self):
        return self.filter(
            is_locked=False,
        )

    def system(self):
        return self.filter(
            is_system=True,
        )

    def not_system(self):
        return self.filter(
            is_system=False,
        )

    def hidden(self):
        return self.filter(
            is_hidden=True,
        )

    def not_hidden(self):
        return self.filter(
            is_hidden=False,
        )


class CommonAggregationMixins(models.QuerySet):

    date_field = "date"

    def sum(self, date_field):
        if not date_field:
            date_field = self.date_field

        return self.aggregate(models.Sum(date_field))[f"{date_field}__sum"]

    def avg(self, date_field):
        if not date_field:
            date_field = self.date_field

        return self.aggregate(models.Avg(date_field))[f"{date_field}__avg"]

    def before(self, date, date_field=None, strict=False):
        """
        Filter the queryset before a date. If no date is provided, return all
        before date is exclusively less than the date
        :param strict: default is False to faciliate chaining it with filters without having to check for None
        :param date:
        :param date_field:
        :return:
        """
        return self._filter_by_date("__lt", date, date_field, strict)

    def after(self, date, date_field=None, strict=False):
        """
        Filter the queryset after a date. If no date is provided, return all unless strict is True
        :param date:
        :param date_field:
        :param strict:
        :return:
        """
        return self._filter_by_date("__gt", date, date_field, strict)

    def upto(self, date, date_field=None, strict=False):
        """
        non-exclusive version of before()
        :param strict:
        :param date:
        :param date_field:
        :return:
        """
        return self._filter_by_date("__lte", date, date_field, strict)

    def from_date(self, date, date_field=None, strict=False):
        return self._filter_by_date("__gte", date, date_field, strict)

    def between(
        self,
        start_date,
        end_date,
        date_field=None,
        strict=True,
    ):
        """
        Filter the queryset between two dates, inclusive
        :param strict:
        :param date_field:
        :param start_date:
        :param end_date:
        :param filters:
        :return:
        """
        qs = self.all()

        if start_date:
            qs = qs.from_date(start_date, date_field, strict)

        if end_date:
            qs = qs.upto(end_date, date_field, strict)

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

    def years(self):
        return self.dates(self.date_field, "year")

    def _filter_by_date(self, lookup, date, date_field, strict=False):
        if not date_field:
            date_field = self.date_field

        if not date:
            return self.none() if strict else self.all()

        return self.filter(**{f"{date_field}{lookup}": date})
