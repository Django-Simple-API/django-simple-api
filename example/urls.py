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

from django_simple_api import mark_tags
from django_simple_api.utils import wrapper_chain, wrapper_urlpatterns

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
    path("test/", wrapper_chain([mark_tags("tag1")], include("tests.urls"))),
    path("test/", wrapper_chain([mark_tags("tag2", "tag3")], include("tests.urls"))),
    path(
        "test/",
        wrapper_chain([mark_tags("tag4"), mark_tags("tag5")], include("tests.urls")),
    ),
]

wrapper_urlpatterns([mark_tags("tag6")], urlpatterns)
