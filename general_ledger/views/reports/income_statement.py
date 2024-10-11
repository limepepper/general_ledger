from datetime import datetime

from bs4 import BeautifulSoup as bs

# import pprint
from django.utils import timezone
from django.views.generic import TemplateView
from rich.console import Console

from general_ledger.helpers.ledger_helper import LedgerHelper
from general_ledger.render.format_statement_j2 import StatementFormatJ2
from general_ledger.render.renderer_statement import StatementRenderer
from general_ledger.statements.meta import NodeMeta
from general_ledger.statements.nodes.income_statement import IncomeStatementNode
from general_ledger.statements.provider_django import DjangoProvider

console = Console()


class IncomeStatementView(TemplateView):
    template_name = "gl/statements/income_statement.html.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["from_date"] = self.request.session.get("from_date", None)
        context["to_date"] = self.request.session.get("to_date", None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        from_date = request.GET.get("from_date") or request.session.get("from_date")
        to_date = request.GET.get("to_date") or request.session.get("to_date")

        if not from_date:
            today = timezone.now().date()
            from_date = today - timezone.timedelta(days=365)
        else:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

        if not to_date:
            today = timezone.now().date()
            to_date = today
        else:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Store the dates in the session
        request.session["from_date"] = from_date.strftime("%Y-%m-%d")
        request.session["to_date"] = to_date.strftime("%Y-%m-%d")

        # print(f"from_date: {from_date}")
        # print(f"to_date: {to_date}")

        # pp(context)

        context["from_date"] = from_date.strftime("%Y-%m-%d")
        context["to_date"] = to_date.strftime("%Y-%m-%d")

        ledger = self.request.active_book.get_default_ledger()

        # ledger = load_chapter_7_review_7_5()
        ledger_accounts = LedgerHelper.ledger_accounts(ledger)

        kwargs = {
            "balance_interval": "month",
            "start_date": "2023-9-1",
            "end_date": "2023-9-30",
            "ledger": ledger,
            "final_balance": True,
        }

        provider = DjangoProvider(ledger=ledger)
        statement = IncomeStatementNode(
            provider=provider,
            meta=NodeMeta(
                show_subtotal=True,
            ),
            label="Income Statement",
            **kwargs,
        ).ensure_expanded()

        statement.set_renderer(StatementRenderer())
        renderer = statement.renderer
        renderer.print_console = False
        renderer.return_renderable = True
        statement.set_render_format(
            "statement",
            StatementFormatJ2(),
        ).render()

        html_rendered = statement.render()

        # console.print(html_rendered)

        soup = bs(html_rendered)

        # console.print(soup.prettify())

        context["statement"] = html_rendered

        return self.render_to_response(context)

    # def post(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #
    #     from_date = request.POST.get('from_date', None)
    #     to_date = request.POST.get('to_date', None)
    #
    #     # Store the dates in the session
    #     request.session['from_date'] = from_date
    #     request.session['to_date'] = to_date
    #
    #     print(f"from_date: {from_date}")
    #     print(f"to_date: {to_date}")
    #
    #     pp(context)
    #
    #     context["from_date"] = from_date
    #     context["to_date"] = to_date
    #
    #
    #     return self.render_to_response(context)
