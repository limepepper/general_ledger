from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def ledger_actions(ledger_id):
    import_url = reverse("admin:ledger_import", args=[ledger_id])
    export_url = reverse("admin:ledger_export", args=[ledger_id])
    validate_url = reverse("admin:ledger_validate", args=[ledger_id])

    return f"""
    <div style="text-align: right;">
        <a class="button" href="{import_url}">Import</a>
        <a class="button" href="{export_url}">Export</a>
        <a class="button" href="{validate_url}">Validate</a>
    </div>
    """
