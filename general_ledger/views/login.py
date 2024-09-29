from allauth.account.views import LoginView


class GeneralLedgerLoginView(LoginView):
    """This view renders our login page."""

    template_name = "gl/login.html.j2"
