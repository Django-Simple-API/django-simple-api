from django.urls import path

from . import views

urlpatterns = [
    path("get-docs/", views.get_docs, name="get-docs"),
    path("cls/<param1>/", views.Home.as_view()),
    path("func/<param1>/", views.func),
]
