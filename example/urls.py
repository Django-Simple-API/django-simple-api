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
from django.urls import include, path

from django_simple_api.extras import mark_tags, mark_tags_for_urlpatterns, deprecated_mark_tags

urlpatterns = [
    # generate documentation
    path(
        "docs/",
        include("django_simple_api.urls"),
        {
            "template_name": "swagger.html",
            "title": "Title",
            "description": "description",
            "version": "version",
        },
    ),
    # unit test
    path("test/", mark_tags("tag1")(include("tests.urls"))),
    path("test/", deprecated_mark_tags(include("tests.urls"), ["tag3"])),
]

mark_tags_for_urlpatterns(urlpatterns, ("tag2",))
