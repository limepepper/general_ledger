from jinja2 import Template

from general_ledger.render.renderer_abc import Renderer


class Jinja2WebRenderer(Renderer):
    def print_intervals(self):
        pass

    def do_render(self):
        pass

    def print_header(self):
        template = Template("[HEADER] Account Summary Report\n")
        print(template.render())

    def print_opening_balance(self):
        template = Template("Opening Balance: {{ opening_balance }}\n")
        print(template.render(opening_balance=self.account_summary.opening_balance))

    def print_entries(self):
        for entry in self.account_summary.entries:
            template = Template("Entry: {{ entry }}\n")
            print(template.render(entry=entry))

    def print_closing_balance(self):
        template = Template(
            "Closing Balance: {{ self.account_summary['suffix']['totals'] }}\n"
        )
        print(template.render(closing_balance=self.account_summary.closing_balance))

    def print_footer(self):
        template = Template("[FOOTER] End of Report\n")
        print(template.render())
