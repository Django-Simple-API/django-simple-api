from django.urls import path

from . import views

app_name = "django_simple_api"

urlpatterns = [
    path("", views.docs, name="docs"),
    path("get-docs/", views.get_docs, name="get_docs"),
    path("get-static/", views.get_static, name="get_static"),
]
