from abc import ABC, abstractmethod

from loguru import logger


class Renderer(ABC):
    def __init__(self):
        self.account_summary = None
        self.return_renderable = False
        self.print_console = True
        self.options = None

    def render(self, renderable_object, **options):
        logger.trace(f"Rendering with {self.__class__.__name__}")
        self.account_summary = renderable_object
        if self.options and hasattr(self.options, "overrides"):
            # self.options = RenderOptions(RendererConfig().get(self.__class__.__name__))
            self.options.overrides = options if options else self.options.overrides
        self.print_header()
        self.print_intervals()
        self.print_footer()
        return self.do_render()

    def print_header(self):
        pass

    @abstractmethod
    def print_intervals(self):
        pass

    def print_footer(self):
        pass

    @abstractmethod
    def do_render(self):
        pass
