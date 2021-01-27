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
Suppose you want to use the `GET` method and accept an argument, you can do this
```python
from django_simple_api import Query, allow_request_method

@allow_request_method("get")
def get_user(request, user_name: str = Query(...)):
    return JsonResponse({"name": user_name})
```
Register the view function in urlpatterns
```python
urlpatterns = [
    ...,
    path("get-user/", get_user),
]
```

`@allow_request_method("get")`Declare the request method allowed by the view function.

`user_name: str = Query(...)` Gets a required `String` parameter `user_name` from a `GET` request parameter.
If the parameter does not exist,the request will be rejected,it will return status code 422 and state the reason.

Of course you can pass in default parameters,`Query("Bill")`
Let's look at another example:
```python
from django_simple_api import Body

@csrf_exempt
@allow_request_method("post")
def add(request, first_num: int = Body(1), second_num: int = Body(2)):
    return JsonResponse({"result": first_num + second_num})
```
Execute the command
```shell script
curl -X POST "http://127.0.0.1:8000/add/" -H  "Content-Type: application/json" -d "{\"first_num\":3}"
```
You'll see response {"result": 5}

It represents getting two non-required parameters of type `integer` from the parameters of the `POST` request,
If the parameter type is `String`,The request will be rejected.

Because you declared `first_num` to be of type hint `int`,
When the parameters are injected, the conversion is done automatically for you,
So `first_num` and `second_num` can be added directly without the need for manual type conversion


Now you open the URL [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)

![](docs/images/show_swagger_index.png)

> You can see the API documentation online,and you can send mock requests on it

![](docs/images/show_test_get.png)


If you want to use multiple request methods in a view, please use class based view,
You can also add description information to the function, which will be displayed in the API documentation

```python
class JustTest(View):
    def get(
        self,
        request: HttpRequest,
        id: int = Path(..., description="This is description of id."),
    ) -> HttpResponse:
        """
        This is summary.

        This is description.
        """
        return HttpResponse(id)
```
Register the View in urlpatterns
```python
urlpatterns = [
    ...,
    path("just-test/<id>", JustTest.as_view()),
]
```
The path parameters `id` will be passed into the view by field Path,and you'll see a lot of descriptions in the API documentation

![](docs/images/show_descriptions.png)

#### All fields that can be injected into a function
| Field name| Explain|
| ---       | ---    |
| Query     | |
| Body      | |
| Path      | |
| Cookie    | |
| Header    | |
| Exclusive | |

#### Field argument explain
| Name           | Explain |
| ---            | ---     |
| default        | since this is replacing the field’s default, its first argument is used to set the default, use ellipsis (``...``) to indicate the field is required|
| default_factory| callable that will be called when a default value is needed for this field. If both `default` and `default_factory` are set, an error is raised.|
| alias          | the public name of the field|
| title          | can be any string, used in the schema|
| description    | can be any string, used in the schema|
| const          | this field is required and *must* take it's default value|
| gt             | only applies to numbers, requires the field to be "greater than". The schema will have an ``exclusiveMinimum`` validation keyword|
| ge             | only applies to numbers, requires the field to be "greater than or equal to". The schema will have a ``minimum`` validation keyword|
| lt             | only applies to numbers, requires the field to be "less than". The schema will have an ``exclusiveMaximum`` validation keyword|
| le             | only applies to numbers, requires the field to be "less than or equal to". The schema will have a ``maximum`` validation keyword|
| multiple_of    | only applies to numbers, requires the field to be "a multiple of". The schema will have a ``multipleOf`` validation keyword|
| min_items      | only applies to list or tuple and set, requires the field to have a minimum length.|
| max_items      | only applies to list or tuple and set, requires the field to have a maximum length.|
| min_length     | only applies to strings, requires the field to have a minimum length. The schema will have a ``maximum`` validation keyword|
| max_length     | only applies to strings, requires the field to have a maximum length. The schema will have a ``maxLength`` validation keyword|
| regex          | only applies to strings, requires the field match again a regular expression pattern string. The schema will have a ``pattern`` validation keyword|
| extra          | any additional keyword arguments will be added as is to the schema|

