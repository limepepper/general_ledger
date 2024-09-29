from jinja2 import Environment
from django.urls import reverse
from django.templatetags.static import static
from django.conf import settings


def environment(**options):
    options.pop("string_if_invalid", None)
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "MEDIA_URL": settings.MEDIA_URL,
        }
    )
    return env
