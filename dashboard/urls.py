from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_jinja import views
from django.conf import settings
from general_ledger.views.utils import ServerResponseSimulator

handler400 = views.BadRequest.as_view()
# handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
# handler500 = views.ServerError.as_view()


urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path("admin/", admin.site.urls),
    # path(
    #     "inbox/notifications/", include("notifications.urls", namespace="notifications")
    # ),
    path("", include(("general_ledger.urls", "general_ledger"))),
    path("accounts/", include("allauth.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    path("api/v1/", include("general_ledger.urls_api")),
    path("500", ServerResponseSimulator.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
