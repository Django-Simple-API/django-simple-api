from django.db import models
from django.apps import AppConfig

from .utils import get_all_urls
from .params import parse_and_bound_params
from .serialize import serialize_model, serialize_queryset


class DjangoSimpleAPIConfig(AppConfig):
    name = "django_simple_api"

    def ready(self):
        models.Model.to_json = serialize_model
        models.query.QuerySet.to_json = serialize_queryset
        models.query.RawQuerySet.to_json = serialize_queryset

        for url_format, http_handler in get_all_urls():
            parse_and_bound_params(http_handler)
