from loguru import logger
from rich.box import Box
from rich.console import Console
from rich.theme import Theme

from general_ledger.render.config_options import RenderOptions, RendererConfig
from general_ledger.render.format_table_rich_t_account import TAccountFormat
from general_ledger.render.formats_abc import TableFormat
from general_ledger.render.renderables import (
    RendererFactory,
)
from general_ledger.render.renderer_abc import Renderer

trial_balance_theme = Theme(
    {
        "trial.table.header": "dim cyan",
    }
)


class RichConsoleRenderer(Renderer):

    def __init__(self, table_format=None, config=None, **options):
        super().__init__()
        self.return_renderable = True
        self.print_console = False
        self.console = Console(theme=trial_balance_theme)
        # @TODO any way to load a default without importing the type?
        self.table_format = table_format or TAccountFormat()
        self.renderable = None  # rich renderable object
        self.config = config or RendererConfig()
        self.options = RenderOptions(
            config=self.config.get("rich", self.table_format.config_key), **options
        )
        # self.context = RendererContext(RenderOptions(config=config, **options))
        self.factory = RendererFactory(self.options)

    def set_table_format(self, table_format, **options):
        logger.trace("setting table format to {}", table_format)
        if not isinstance(table_format, TableFormat):
            raise ValueError("Table format must be an instance of TableFormat")
        self.table_format = table_format
        self.options.overrides.update(options)
        self.options = RenderOptions(
            config=self.config.get("rich", self.table_format.config_key),
            **self.options.overrides,
        )
        return self

    def print_intervals(self):
        if not self.table_format:
            raise ValueError("table_format not set")
        self.table_format.render_table(self, self.account_summary)

    def do_render(self):
        if self.print_console:
            self.console.print(self.renderable)
        if self.return_renderable:
            return self.renderable
