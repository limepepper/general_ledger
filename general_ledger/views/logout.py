from allauth.account.views import LogoutView


class GeneralLedgerLogoutView(LogoutView):
    """This view renders our logout page."""

    template_name = "gl/logout.html.j2"
