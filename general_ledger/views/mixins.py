import logging
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from loguru import logger


class GeneralLedgerSecurityMixIn(
    LoginRequiredMixin,
):
    """
    Mixin that requires the user to be authenticated.
    """

    login_url = reverse_lazy("general_ledger:account_login")


isEditablelogger = logging.getLogger("general_ledger.views.mixins.IsEditableMixin")


class IsEditableMixin:
    """
    Mixin that requires the user to be authenticated and the entity to be editable.
    If the entity is not editable, redirects to the entity detail page.
    """

    def dispatch(self, request, *args, **kwargs):
        isEditablelogger.critical(f"IsEditableMixin - calling dispatch")
        self.object = self.get_object()
        if self.object and not self.object.can_edit():
            messages.warning(
                request, "This object cannot be edited in its current state."
            )
            return redirect(self.object.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_detail_url(self):
        """
        Returns the URL to redirect to if the entity is not editable.
        Override this method if the URL pattern name is different or requires arguments.
        """
        if not self.detail_url:
            raise ImproperlyConfigured(
                "IsEditableMixin requires a definition of 'detail_url' or an implementation of 'get_detail_url()'."
            )
        return self.detail_url


activeBookRequiredMixinLogger = logging.getLogger(f"{__name__}.ActiveBookRequiredMixin")


class ActiveBookRequiredMixin(ContextMixin):
    """
    Mixin that requires an active entity to be set in the session.
    If no active entity is found, redirects to the entity selection page.
    """

    select_entity_url = "general_ledger:select_active_entity"
    redirect_field_name = "next"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("active_book_pk"):
            return self.handle_no_activebook()
        return super().dispatch(request, *args, **kwargs)

    # @TODO write test to verify this is working with various
    # nasty stuff in the ?next= parameter
    def handle_no_activebook(self):
        path = self.request.build_absolute_uri()
        resolved_url = resolve_url(self.get_select_entity_url())
        login_scheme, login_netloc = urlparse(resolved_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            path = self.request.get_full_path()
        return redirect_to_login(
            path,
            resolved_url,
            self.redirect_field_name,
        )

    def get_context_data(self, **kwargs):
        """
        Adds the active entity to the context.
        """
        logger.debug(
            f"ActiveBookRequiredMixin : {'get_context_data' : >20} (start) - kwargs: {kwargs}"
        )
        activeBookRequiredMixinLogger.debug(
            f"ActiveBookRequiredMixin start get_context_data1"
        )
        data = super().get_context_data(**kwargs)
        data["active_book"] = self.request.active_book
        activeBookRequiredMixinLogger.debug(
            f"ActiveBookRequiredMixin get_context_data returning {data}"
        )
        logger.debug(
            f"ActiveBookRequiredMixin : {'get_context_data' : >20} (returning) - data: {data}"
        )
        return data

    def get_select_entity_url(self):
        """
        Returns the URL to redirect to if no active entity is set.
        Override this method if the URL pattern name is different or requires arguments.
        """
        if not self.select_entity_url:
            raise ImproperlyConfigured(
                "ActiveEntityRequiredMixin requires a definition of 'select_entity_url' or an implementation of 'get_select_entity_url()'."
            )
        return self.select_entity_url


class FormsetifyMixin(ContextMixin):

    extra_context = {
        "click_actions": "disable -> submit({add: true}) -> proceed !~ scrollToError",
        "click_actions_update": "disable -> submit({update: true}) -> proceed !~ scrollToError",
        "click_actions_delete": "disable -> submit({delete: true}) -> proceed !~ scrollToError",
        "button_css_classes": "mt-4",
    }

    def get_success_url(self):
        """
        Returns the URL to redirect to after processing a valid form.
        """
        if getattr(self, "success_url", False):
            return self.success_url
        if self.object:
            return self.object.get_absolute_url()
        return self.request.path()
