**Language: English | [Chinese](README.zh-CN.md)**

# Django Simple API

A non-intrusive component that can help you quickly create APIs.

## Quick Start

### Install

Download and install from github:

```
pip install django-simple-api
```

### Configure

Add django-simple-api to your `INSTALLED_APPS` in settings:

```python
INSTALLED_APPS = [
    ...,
    "django_simple_api",
]
```

Register the middleware to your `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    ...,
    "django_simple_api.middleware.SimpleApiMiddleware",
]
```

Add the url of ***django-simple-api*** to your urls.py:

```python
# urls.py

from django.urls import include, path
from django.conf import settings

# Your urls
urlpatterns = [
    ...
]

# Simple API urls, should only run in a test environment.
if settings.DEBUG:
    urlpatterns += [
        # generate documentation
        path("docs/", include("django_simple_api.urls"))
    ]
```

### Complete the first example

Define your url:

```python
# your urls.py

from django.urls import path
from yourviews import JustTest

urlpatterns = [
    ...,
    path("/path/<int:id>/", JustTest.as_view()),
]
```

Define your view:

```python
# your views.py

from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Query


class JustTest(View):
    def get(self, request, id: int = Query()):
        return HttpResponse(id)
```

> ⚠️ To generate the document, you must declare the parameters according to the  rules of ***Simple API*** (like the example above).
>
> Click [Declare parameters](https://django-simple-api.aber.sh/declare-parameters/) to see how to declare parameters.

### Access interface document

After the above configuration, you can start your server and access the interface documentation now.

If your service is running locally, you can visit [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/) to view
your documentation.

## More

For more tutorials, see [Django Simple API](https://django-simple-api.aber.sh/).
