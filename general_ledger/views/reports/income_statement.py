from pprint import pprint

from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.http import Http404
# import pprint
from pprint import pprint, pp
from django.utils import timezone
from datetime import datetime

class IncomeStatementView(TemplateView):
    template_name = "gl/income_statement.html.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["from_date"] = self.request.session.get('from_date', None)
        context["to_date"] = self.request.session.get('to_date', None)
        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        from_date = request.GET.get('from_date') or request.session.get('from_date')
        to_date = request.GET.get('to_date') or request.session.get('to_date')


        if not from_date:
            today = timezone.now().date()
            from_date = today.replace(month=1, day=1)
        else:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()

        if not to_date:
            today = timezone.now().date()
            to_date = today
        else:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

        # Store the dates in the session
        request.session['from_date'] = from_date.strftime('%Y-%m-%d')
        request.session['to_date'] = to_date.strftime('%Y-%m-%d')

        print(f"from_date: {from_date}")
        print(f"to_date: {to_date}")

        #pp(context)

        context["from_date"] = from_date.strftime('%Y-%m-%d')
        context["to_date"] = to_date.strftime('%Y-%m-%d')

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
