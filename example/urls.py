"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/", include("django_simple_api.urls")),
    path("just-test/<id>", views.JustTest.as_view()),
    path("test-get-func/<name>", views.get_func),
    path("test-post-func/<name>", views.post_func),
    path("test-put-func/<id>", views.put_func),
    path("test-delete-func/<id>", views.test_delete_func),
    path("test-query-page", views.query_page),
    path("test-query-page-by-exclusive", views.query_page_by_exclusive),
    path("test-common-func-view", views.test_common_func_view),
    path("test-common-func-view/<id>", views.test_common_path_func_view),
    path("test-common-class-view", views.CommonClassView.as_view()),
]
