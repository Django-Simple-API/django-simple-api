from django.urls import path

from . import views

urlpatterns = [
    path("", views.docs, name="docs"),
    path("get-docs/", views.get_docs, name="get_docs"),
]
