from loguru import logger
from rich.console import Console

from general_ledger.render.config_options import RenderOptions, RendererConfig
from general_ledger.render.format_statement_rich_table import StatementFormatRichTable
from general_ledger.render.formats_abc import StatementFormat
from general_ledger.render.renderer_abc import Renderer

logger = logger.opt(colors=True)
console = Console()


class StatementRenderer(Renderer):
    """Renders hierarchical statement nodes with running totals"""

    def __init__(
        self,
        statement_format=None,
        config=None,
        print_console=False,
        return_renderable=True,
        **options,
    ):
        super().__init__()
        self.return_renderable = return_renderable
        self.print_console = print_console
        self.console = Console()
        # self.context = StatementRenderingContext()
        self.statement_format = statement_format or StatementFormatRichTable()
        self.config = config or RendererConfig()
        self.options = RenderOptions(
            config=self.config.get("rich", self.statement_format.config_key),
            **options,
        )
        self.renderable = None  # rich renderable object

    def set_statement_format(self, value, **options):
        if not isinstance(value, StatementFormat):
            raise ValueError("format must be an instance of StatementFormat")
        self.statement_format = value
        self.options.overrides.update(options)

    def print_intervals(self):
        if not self.statement_format:
            raise ValueError("statement_format not set")
        return self.statement_format.render_statement(self, self.account_summary)

    def do_render(self):
        if self.print_console:
            logger.trace("printing console")
            self.console.print(self.renderable)
        if self.return_renderable:
            logger.trace("returning renderable")
            return self.renderable

    def set_render_options(self, options):
        self.options = options
