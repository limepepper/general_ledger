from django.views.debug import ExceptionReporter
from pathlib import Path

from dashboard.settings import BASE_DIR


class MyExceptionReporter(ExceptionReporter):
    @property
    def html_template_path(self):
        return Path(BASE_DIR / "general_ledger/templates/debug/technical_500.html")
