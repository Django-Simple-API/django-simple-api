# Django Simple API

A non-intrusive component that can help you quickly create APIs.

## Install

Download and install from github

```
pip install git+https://github.com/abersheeran/django-simple-api.git@setup.py
```

Add django-simple-api to your `INSTALLED_APPS` in settings:

```python
INSTALLED_APPS = [
    ...
    "django_simple_api",
]
```

Add `SimpleApiMiddleware` to your `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    ...
    "django_simple_api.middleware.SimpleApiMiddleware",
]
```

## Usage
### Parameter declaration and verification
Simple API use `pydantic` to declare parameters and parameter verification.

You can declare request parameters like the following example:
```python
# views.py
from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Query

class JustTest(View):
    def get(self, request, id: int = Query(...)):  
        return HttpResponse(id)
```
Use `Query(...)`  to declare the parameter, which means this parameter is required. If there is no `id` parameter in the query string for url, an error will be returned:
```shell script
[
    {
        "loc": [
            "id"
        ],
        "msg": "field required",
        "type": "value_error.missing"
    }
]
```
In addition, you can use default parameters like this:
```python
class JustTest(View):
    def get(self, request, id: int = Query(10)):  
        return HttpResponse(id)
    # Or
    def get(self, request, id: int = Query(None)):  
        return HttpResponse(id)
```
Or you can use the `default_factory` parameter and pass in a function to dynamically calculate the default value:
```python
def func():
    return 1000

class JustTest(View):
    def get(self, request, id: int = Query(default_factory=func)): 
        print(id)  # 1000
        return HttpResponse(id)
```
But you cannot use `default` and `default_factory` at the same time, otherwise an error will be reported:
```shell script
ValueError: cannot specify both default and default_factory
```







#### To be continued ...
