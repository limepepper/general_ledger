from django.db import models
from django.db import models
from rich.console import Console
from rich.console import ConsoleOptions, RenderResult

from general_ledger.render.utility_rich import model_table_generator


class TransactionQuerySet(models.QuerySet):
    def posted(self):
        return self.filter(is_posted=True)

    def unposted(self):
        return self.filter(is_posted=False)

    def locked(self):
        return self.filter(is_locked=True)

    def unlocked(self):
        return self.filter(is_locked=False)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from model_table_generator(self, self.model)
