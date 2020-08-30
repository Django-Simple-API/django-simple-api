from django.conf import settings


def urlconf():
    return __import__(settings.ROOT_URLCONF, {}, {}, [""])
