from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django_filters.views import FilterView
from django import template


def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False


class GenericListView(ListView):
    def get_template_names(self):
        if (
            hasattr(self, "template_name")
            and self.template_name
            and template_exists(self.template_name)
        ):
            return [self.template_name]
        return [
            f"gl/{self.model._meta.model_name}/{self.model._meta.model_name}_list.html.j2",
            f"gl/generic/generic_list.html.j2",
        ]

    def get_queryset(self):
        return self.model.objects.for_book(self.request.active_book)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if hasattr(self.model, "generic_list_display"):
            context_data["list_display"] = self.model.generic_list_display
        elif hasattr(self.model, "list_display"):
            context_data["list_display"] = self.model.list_display
        else:
            modeladmin = admin.site._registry[self.model]
            if modeladmin:
                context_data["list_display"] = modeladmin.list_display
        return context_data


class GenericDetailView(DetailView):
    def get_template_names(self):
        return [
            f"gl/{self.model._meta.model_name}/{self.model._meta.model_name}_detail.html.j2",
            f"gl/generic/generic_detail.html.j2",
        ]

    def get_queryset(self):
        return self.model.objects.for_book(self.request.active_book)

    def get_context_data(self, **kwargs):
        """
        the purpose of this I think weas to pass the list_display to the generic template
        :param kwargs:
        :return:
        """
        context_data = super().get_context_data(**kwargs)
        modeladmin = admin.site._registry[self.model]
        context_data["modeladmin"] = modeladmin
        return context_data
