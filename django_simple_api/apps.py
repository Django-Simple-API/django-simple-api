from django.apps import AppConfig

from .utils import get_urls
from .params import parse_and_bound_params


class DjangoSimpleAPIConfig(AppConfig):
    name = "django_simple_api"

    def ready(self):
        for url_format, http_handler in get_urls():
            parse_and_bound_params(http_handler)
