import json

from django.forms.renderers import get_default_renderer
from django.utils.module_loading import import_string
from formset.views import FormCollectionViewMixin
from loguru import logger

from general_ledger.utils import JSONEncoder


class SessionFormCollectionMixin:

    # def get_queryset(self):
    #     if not self.request.session.session_key:
    #         self.request.session.cycle_key()
    #     queryset = super().get_queryset()
    #     qs = queryset.filter(created_by=self.request.session.session_key)
    #     logger.debug(f"Happy logging with Loguru! - {qs=}")
    #     return qs

    # def get_object(self, queryset=None):
    #     logger.debug(f"Happy logging with Loguru! - {queryset=}")
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #     if object := queryset.last():
    #         return object
    #
    #     obj = self.model(created_by=self.request.session.session_key)
    #     return obj

    def form_collection_valid(self, form_collection):
        logger.debug("SessionFormCollectionMixin : form_collection_valid")
        return super().form_collection_valid(form_collection)


class CollectionViewMixin(FormCollectionViewMixin):
    def get_css_classes(self):
        css_classes = dict(demo_css_classes[self.framework].get("*", {}))
        css_classes.update(demo_css_classes[self.framework].get(self.mode, {}))
        return css_classes

    @property
    def mode(self):
        if self.request.resolver_match.url_name:
            return self.request.resolver_match.url_name.split(".")[-1]

    def get_collection_class(self):
        collection_class = super().get_collection_class()
        attrs = self.get_css_classes()
        attrs.pop("button_css_classes", None)
        renderer_class = import_string(f"formset.renderers.bootstrap.FormRenderer")
        collection_class.default_renderer = renderer_class(**attrs)
        return collection_class

    def get_form_collection(self):
        """
        This method replaces the form renderer by a specialized version which is specified in css_classes.
        Used to show how to style forms nested inside collections.
        """

        def traverse_holders(declared_holders, path=None):
            for name, holder in declared_holders.items():
                key = f"{path}.{name}" if path else name
                # print(f"traverse_holders: {name=}, {holder=} {key=}")

                holder.active_book_id = self.active_book_id

                if hasattr(holder, "declared_holders"):
                    logger.debug(f"recursing into {name=}")
                    traverse_holders(holder.declared_holders, key)
                elif key in css_classes:
                    logger.debug(f"setting renderer for {key=}")
                    holder.renderer = form_collection.default_renderer.__class__(
                        **css_classes[key]
                    )
                else:
                    holder.renderer = get_default_renderer()

        css_classes = demo_css_classes[self.framework]
        # logger.debug(f"{css_classes=}")

        form_collection = super().get_form_collection()
        logger.debug(f"{form_collection=}")

        traverse_holders(form_collection.declared_holders)
        return form_collection

    def form_collection_valid(self, form_collection):
        logger.debug("form_collection_valid : start")
        logger.debug("form_collection_valid")
        formset_data = json.loads(self.request.body)["formset_data"]
        self.request.session["valid_formset_data"] = json.dumps(
            formset_data, cls=JSONEncoder, indent=2, ensure_ascii=False
        )
        logger.debug(f"{self.request.body=}")
        result = super().form_collection_valid(form_collection)
        logger.debug("form_collection_valid : retruning {result=}")
        return result


demo_css_classes = {
    "default": {"*": {}},
    "bootstrap": {
        "*": {
            "field_css_classes": {
                "*": "mb-2",
                "submit": "d-grid col-3",
                "reset": "d-grid col-3",
            },
            "fieldset_css_classes": "border p-3",
            "button_css_classes": "mt-4",
        },
        "invoice": {
            "form_css_classes": "row",
            "field_css_classes": {
                "*": "mb-2 col-12",
                "contact": "col-3",
                "ledger": "col-3",
                "invoice_number": "col-3",
                "description": "col-3",
                "date": "col-3",
                "due_date": "col-3",
                "tax_inclusive": "col-3",
                "submit": "d-grid col-3 xxxx",
                "reset": "d-grid col-3 xxx",
            },
        },
        "invoice_lines": {
            "field_css_classes": {
                "*": "mb-2 col-12",
                "quantity": "mb-2 col-2",
                "unit_price": "mb-2 col-2 wank",
                "vat_rate": "mb-2 col-2",
                "name": "mb-2 col-2",
                "description": "mb-2 col-2",
                "submit": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
                "reset": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
            },
            "max_options_per_line": 2,
            "collection_css_classes": "dummy1 dummy2",
        },
        "invoice_lines.invoice_line": {
            "form_css_classes": "row",
            "field_css_classes": {
                "*": "mb-2 col-12",
                "quantity": "mb-2 col-2",
                "unit_price": "mb-2 col-2 invoice-line-number-field",
                "vat_rate": "mb-2 col-2",
                "name": "mb-2 col-2",
                "description": "mb-2 col-2",
                "submit": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
                "reset": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
            },
            "collection_css_classes": "dummy1 dummy2",
            "control_css_classes": "control_css_classes",
        },
        "address": {
            "form_css_classes": "row",
            "field_css_classes": {
                "*": "mb-2 col-12",
                "postal_code": "mb-2 col-4",
                "city": "mb-2 col-8",
                "submit": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
                "reset": "d-grid col-6 col-md-5 col-lg-4 col-xl-3",
            },
        },
        "horizontal": {
            "field_css_classes": "row mb-3",
            "label_css_classes": "col-sm-3",
            "control_css_classes": "col-sm-9",
            "button_css_classes": "offset-sm-3",
        },
        "page": {
            "form_css_classes": "row",
            "field_css_classes": {
                "*": "mb-2 col-12",
                "reporter": "mb-2 col-lg-8 col-md-6",
                "edit_reporter": "mt-4 pt-2 col-lg-2 col-md-3",
                "add_reporter": "mt-4 pt-2 col-lg-2 col-md-3",
            },
        },
        "simplecontact": {
            "form_css_classes": "row",
            "field_css_classes": {
                "*": "col-12 mb-2",
                "profession.company": "col-6 mb-2",
                "profession.job_title": "col-6 mb-2",
            },
        },
        "numbers.number": {
            "form_css_classes": "row",
            "field_css_classes": {
                "phone_number": "mb-2 col-8",
                "label": "mb-2 col-4",
                "*": "mb-2 col-12",
            },
        },
        # 'terms_of_use': {
        #     'field_css_classes': {
        #         '*': 'mb-2 col-12',
        #         'submit': 'd-grid col-3',
        #         'reset': 'd-grid col-3',
        #     },
        # },
    },
}
