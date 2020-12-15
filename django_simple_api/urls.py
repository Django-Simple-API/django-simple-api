from django.urls import path

from . import views

urlpatterns = [
    path("get-docs", views.get_docs, name="get-docs"),
    path("", views.redoc),
]
