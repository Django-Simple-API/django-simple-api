**Hints:**
If you want to automatically generate interface documentation, you must add the url of ***Simple API*** to your urls.py, See [Quick Start](quick-start.md).

## Modify the interface document description information
You can modify the interface document description information in the url of `Simple API`, like this:

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
        path(
            "docs/",
            include("django_simple_api.urls"),
            {
                "template_name": "swagger.html",
                "title": "Django Simple API",
                "description": "This is description of your interface document.",
                "version": "0.1.0",
            },
        ),
    ]
```

In the above example, you can modify the `template_name` to change the UI theme of the interface document, We currently have two UI themes: `swagger.html` and `redoc.html`.

And then you can modify `title`、`description` and `version` to describe your interface documentation.


## Generate documentation for `function-view`
If you are using `class-view`, you can now generate documentation. 
Start your service, if your service is running locally, you can visit [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/) to view your documentation.

But if you are using `view-function`, you must declare the request method supported by the view function:

```python
# views.py

from django_simple_api import allow_request_method

@allow_request_method("get")
def just_test(request, id: int = Query()):
    return HttpResponse(id)
```

`allow_request_method` can only declare one request method, and it must be in `['get', 'post', 'put', 'patch', 'delete', 'head', 'options', trace']`.
We do not support the behavior of using multiple request methods in a `view-function`, which will cause trouble for generating documentation.

Note that if you use `@allow_request_method("get")` to declare a request method, you will not be able to use request methods other than `get`, otherwise it will return `405 Method Not Allow`.

You can also not use `allow_request_method`, this will not have any negative effects, but it will not generate documentation.
We will use `warning.warn()` to remind you, this is not a problem, just to prevent you from forgetting to use it.

Now, the `view-function` can also generate documents, you can continue to visit your server to view the effect.


## Improve documentation information
***Simple API*** is generated according to the [`OpenAPI`](https://github.com/OAI/OpenAPI-Specification) specification. 
In addition to automatically generating function parameters, you can also manually add some additional information to the view yourself, 
for example: `summary` `description` `responses` and `tags`.

### Add `summary` and `description` to the view
`summary` and `description` can describe the information of your interface in the interface document, `summary` is used to briefly introduce the function of the interface, and `description` is used to describe more information.

There must be a blank line between `summary` and `description`. If there is no blank line, then all `doc` will be considered as `summary`.

```python
# views.py

class JustTest(View):
    def get(self, request, id: int = Query()):
        """
        This is summary.

        This is description ...
        This is description ...
        """
        return HttpResponse(id)
```

### Add `responses` to the view
`responses` is also important information in the interface documentation.
You can define the response information that the interface should return in various situations.

***Simple API*** highly recommends using `pydantic.BaseModel` to define the data structure of the response message, for example:

```python
# views.py

from typing import List

from pydantic import BaseModel
from django.views import View

from django_simple_api import describe_response


# define the data structure for `response`
class JustTestResponses(BaseModel):
    code: str
    message: str
    data: List[dict]


class JustTest(View):
    
    # describe the response information of the interface
    @describe_response(200, content=JustTestResponses)
    def get(self, request, id: int = Query()):

        # actual response data(just an example)
        resp = {
            "code": "0",
            "message": "success",
            "data": [
                {"id": 0, "name": "Tom"},
                {"id": 1, "name": "John"},
            ]
        }
        return JsonResponse(resp)
```

Then the interface document will show:

```shell
{
  "code": "string",
  "message": "string",
  "data": [
    {}
  ]
}
```

You can also show the example in the interface document, you only need to add the example to the `BaseModel` and it will be shown in the interface document:

```python
# views.py

class JustTestResponses(BaseModel):
    code: str
    message: str
    data: List[dict]
    
    class Config:
        schema_extra = {
            "example": {
                "code": "0",
                "message": "success",
                "data": [
                    {"id": 0, "name": "Tom"},
                    {"id": 1, "name": "John"},
                ]
            }
        }

class JustTest(View):
    
    @describe_response(200, content=JustTestResponses)
    def get(self, request, id: int = Query()):
        resp = {...}
        return JsonResponse(resp)
```

Then the interface document will show:

```shell
{
  "code": "0",
  "message": "success",
  "data": [
    {
      "id": 0,
      "name": "Tom"
    },
    {
      "id": 1,
      "name": "John"
    }
  ]
}
```

The default response type of ***Simple API*** is `application/json`, if you want to set other types, you can use it like this:

```python
# views.py

class JustTest(View):
    
    @describe_response(401, content={"text/plain":{"schema": {"type": "string", "example": "No permission"}}})
    def get(self, request, id: int = Query()):
        return JsonResponse(id)
```

Although we support custom response types and data structures, we recommend that you try not to do this, unless it is a very simple response as in the example,
otherwise it will take up a lot of space in your code files and it will not conducive to other people in the team to read the code.

If you need to describe multiple responses, then we will recommend you to use `describe_responses`, which can describe multiple response states at once, 
this is equivalent to using multiple `describe_response` simultaneously:

```python
# views.py

from django_simple_api import describe_responses

class JustTestResponses(BaseModel):
    code: str
    message: str
    data: List[dict]


class JustTest(View):
    
    @describe_responses({
            200: {"content": JustTestResponses},
            401: {"content": {"text/plain": {"schema": {"type": "string", "example": "No permission"}}}}
        })
    def get(self, request, id: int = Query()):
        return JsonResponse(id)
```

> Add `responses` to multiple views simultaneously: [wrapper_include](document-generation.md#wrapper_include)


### Add `tags` to the view

Tagging interfaces is a good way to manage many interfaces, That's how you tag a view:

```python
from django_simple_api import mark_tags, allow_request_method, Query

@mark_tags("about User")
@allow_request_method("get")
def get_name(request, id: int = Query(...)):
    return HttpResponse(get_name_by_id(id))
```

You can use `@mark_tags("tag1", "tag2")` to tag a view with multiple tags

> Add `tags` to multiple views simultaneously: [wrapper_include](document-generation.md#wrapper_include)

## Extensions function

### `wrapper_include`

We also support tagging multiple URLs at the same time

```python
from django_simple_api import wrapper_include, mark_tags

urlpatterns = [
    ...,
    path("app/", wrapper_include([mark_tags("demo tag")], include("app.urls"))),
]
```

The `wrapper_include` in the above code will add `mark_tags` decorators to all views configured in the app URLs

You can also use the `wrapper_include` based functionality

```python
wrapper_include([mark_tags("demo tag"), describe_response(200, "ok")], include("app.urls"))
```

### `describe_extra_docs`

### Support for JSON requests

### To be continue ...
