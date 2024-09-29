from typing import Any, Sequence

from django import http
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.utils import unquote
from django.contrib.auth import get_permission_codename, get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render
from django.urls import re_path, reverse
from django.utils.encoding import force_str
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from simple_history.manager import HistoryManager, HistoricalQuerySet
from simple_history.models import HistoricalChanges
from simple_history.template_utils import HistoricalRecordContextHelper


class HistoryView:

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        # request.current_app = self.admin_site.name
        request.current_app = "general_ledger"
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = unquote(object_id)
        historical_records = self.get_history_queryset(
            request, history, pk_name, object_id
        )
        history_list_display = self.get_history_list_display(request)
        # If no history was found, see whether this object even exists.
        try:
            obj = self.get_queryset(request).get(**{pk_name: object_id})
        except model.DoesNotExist:
            try:
                obj = historical_records.latest("history_date").instance
            except historical_records.model.DoesNotExist:
                raise http.Http404

        if not self.has_view_history_or_change_history_permission(request, obj):
            raise PermissionDenied

        # Set attribute on each historical record from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        self.set_history_delta_changes(request, historical_records)

        content_type = self.content_type_model_cls.objects.get_for_model(
            get_user_model()
        )
        admin_user_view = "admin:{}_{}_change".format(
            content_type.app_label,
            content_type.model,
        )

        context = {
            "title": self.history_view_title(request, obj),
            "object_history_list_template": self.object_history_list_template,
            "historical_records": historical_records,
            "module_name": capfirst(force_str(opts.verbose_name_plural)),
            "object": obj,
            "root_path": getattr(self.admin_site, "root_path", None),
            "app_label": app_label,
            "opts": opts,
            "admin_user_view": admin_user_view,
            "history_list_display": history_list_display,
            "revert_disabled": self.revert_disabled(request, obj),
        }
        context.update(self.admin_site.each_context(request))
        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )

    @staticmethod
    def get_history_queryset(
        request, history_manager: HistoryManager, pk_name: str, object_id: Any
    ) -> QuerySet:
        """
        Return a ``QuerySet`` of all historical records that should be listed in the
        ``object_history_list_template`` template.
        This is used by ``history_view()``.

        :param request:
        :param history_manager:
        :param pk_name: The name of the original model's primary key field.
        :param object_id: The primary key of the object whose history is listed.
        """
        qs: HistoricalQuerySet = history_manager.filter(**{pk_name: object_id})
        if not isinstance(history_manager.model.history_user, property):
            # Only select_related when history_user is a ForeignKey (not a property)
            qs = qs.select_related("history_user")
        # Prefetch related objects to reduce the number of DB queries when diffing
        qs = qs._select_related_history_tracked_objs()
        return qs

    @staticmethod
    def set_history_delta_changes(
        request,
        historical_records: Sequence[HistoricalChanges],
        foreign_keys_are_objs=True,
        model=None,
    ):
        """
        Add a ``history_delta_changes`` attribute to all historical records
        except the first (oldest) one.

        :param request:
        :param historical_records:
        :param foreign_keys_are_objs: Passed to ``diff_against()`` when calculating
               the deltas; see its docstring for details.
        """
        previous = None
        for current in historical_records:
            if previous is None:
                previous = current
                continue
            # Related objects should have been prefetched in `get_history_queryset()`
            delta = previous.diff_against(
                current, foreign_keys_are_objs=foreign_keys_are_objs
            )
            helper = HistoryView.get_historical_record_context_helper(
                model, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current

    def get_historical_record_context_helper(
        model, request, historical_record: HistoricalChanges
    ) -> HistoricalRecordContextHelper:
        """
        Return an instance of ``HistoricalRecordContextHelper`` for formatting
        the template context for ``historical_record``.
        """
        return HistoricalRecordContextHelper(model, historical_record)
