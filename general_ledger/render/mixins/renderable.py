from general_ledger.render.renderer_abc import Renderer


class RenderableMixin:

    renderer: Renderer = None

    def render(self):
        if not self.renderer:
            raise ValueError(f"No renderer set for '{self}'")
        return self.renderer.render(self)

    def set_table_format(self, table_format, **options):
        if hasattr(self.renderer, "set_table_format"):
            self.renderer.set_table_format(table_format, **options)
        else:
            raise ValueError(
                f"Renderer {self.renderer} does not support table format '{table_format}' set_table_format"
            )
        return self

    def set_render_format(self, render_format, value, **options):
        if hasattr(self.renderer, f"set_{render_format}_format"):
            func = getattr(self.renderer, f"set_{render_format}_format")
            func(value, **options)
        else:
            raise ValueError(
                f"Renderer {self.renderer} does not support format '{render_format}' with value '{value}' set_{render_format}_format"
            )
        return self

    def set_renderer(self, renderer: Renderer):
        if not isinstance(renderer, Renderer):
            raise ValueError("Renderer must be an instance of a Renderer")
        self.renderer = renderer
        return self
