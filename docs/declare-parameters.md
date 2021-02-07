Parameter declaration is the infrastructure of ***Simple API***. Whether you want to automatically verify request parameters or automatically generate interface documents, you must first learn how to declare parameters.

You can declare request parameters like the following example:

```python
# views.py

from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Query

class JustTest(View):
    def get(self, request, 
            # `id` is your parameter name.
            # `int` is your parameter type.
            # `Query` represents where your parameters are located,
            # and can describe various information about your parameters.
            id: int = Query()
        ):
        return HttpResponse(id)
```


## Fields
***Simple API*** has a total of 6 fields, corresponding to the parameters in different positions:
##### All fields and description
| Field     | Description |
| ---       | ---         |
| Query     | Indicates that this parameter is in the url query string. example: http://host/?param=1|
| Path      | Indicates that this parameter is a url path parameter. example: http://host/{param}/|
| Body      | Indicates that this parameter is in the request body, and the value can only be obtained in a non-GET request.|
| Cookie    | Indicates that this parameter is in Cookie.|
| Header    | Indicates that this parameter is in Header.|
| Exclusive | This is a special field, its parameter type should be subclass of `pydantic.BaseModel`, it will get all the parameters from the location specified by `Exclusive`.

For example:

```python
# urls.py

urlpatterns = [
        ...
        path("/path/<param2>/<param3>/", JustTest.as_view(), name="path_name"),
    ]
```

```python
# views.py

from django_simple_api import Query, Path, Body, Cookie, Header


class JustTest(View):
    # The parameter names used in the above examples are for demonstration only.
    def post(self, request,
            param1: int = Query(),
            # You can use the same field to describe multiple parameters.
            param2: int = Path(),
            param3: int = Path(),
            param4: str = Body(),
            userid: int = Cookie(alias="uid"),
            username: int = Cookie(alias="username"),
            csrf_token: str = Header(alias="X-CSRF-TOKEN"),
        ):

        return HttpResponse(d)
```

> ⚠️ In the above example, you have two things to note:
>
> * If you have more than one parameter in a field, you can use the field multiple times to describe different parameters (except for the 'Exclusive' field).
> * When you need to get parameters from `Header`, you may need to use `alias` to indicate the request header you want to get, because the name of the request header may not be a valid python identifier.

`Exclusive` is a special field that can obtain all the parameters required by the entire data model from a specified location at one time.

Here's has a example of how to combine `Exclusive` with`Django Model`, now suppose you have the following Model:

```python
# models.py

from django.db import models

class UserModel(models.Model):
    name = models.CharField(max_length=25)
    age = models.SmallIntegerField(default=19)
```

You can use `pydantic.BaseModel` to define a `"Form"`，
Then use the `Exclusive` field to get all parameters required for `"Form"` from the `body`:


```python
# views.py

from django.views import View
from pydantic import BaseModel, Field

from django_simple_api import Exclusive


# Use `pydantic.BaseModel` to define a `"Form"`
class UserForm(BaseModel):
    name: str = Field(max_length=25, description="This is user's name")
    age: int = Field(19, description="This is user's age")


class UserView(View):
    def post(self, request, 
            # Use the `Exclusive` field to get all parameters required for `"Form"` from the `body`:
            user: UserForm = Exclusive(name="body")
        ):

        # You can get the parameters from the "Form" like this:
        name = user.name
        age = user.age
        
        # Also convert the form into a dictionary:
        user.dict()  # {"name": ..., "age": ...}
        
        # So you can directly instantiate the UserModel like this:
        UserModel(**user.dict()).save()

        return HttpResponse("success")
```
> ⚠️ Note, when you use `Exclusive("body")` to get the form from a specified location, you can no longer use the `Body` field, but use of other fields will not be affected.

>There are other uses of `BaseModel`, see [`pydantic`](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict) for more details.


## Type conversion
As you can see in the above example, ***Simple API*** also has the function of type conversion. If the parameter you pass in is legal for the declared type, it will be converted to the declared type without manual operation:

```python
# views.py

class JustTest(View):
    def get(self, request, last_time: datetime.date = Query()):
        print(last_time, type(last_time))
        # 2008-08-08 <class 'datetime.date'>
        return HttpResponse(last_time)
```


## Field properties
Use `Query()`  to declare the parameter, which means this parameter is required. If there is no `id` parameter in the query string for url, an error will be returned:

```shell
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

In addition to this, you can use default parameters like this:

```python
# views.py

class JustTest(View):
    def get(self, request, id: int = Query(10)):
        return HttpResponse(id)

    # equivalent to

    def get(self, request, id: int = Query(default=10)):
        return HttpResponse(id)
```

Or you can use the `default_factory` parameter and pass in a function to dynamically calculate the default value:

```python
# views.py

def func():
    return 1000

class JustTest(View):
    def get(self, request, id: int = Query(default_factory=func)):
        print(id)  # 1000
        return HttpResponse(id)
```

But you cannot use `default` and `default_factory` at the same time, otherwise an error will be reported:

```shell
ValueError: cannot specify both default and default_factory
```

In addition to the `default`、`default_factory`, you can also use more attributes to constrain parameters, such as:

```python
# views.py

class JustTest(View):
    # Use `const` to constrain the parameter value must be the same as the default value
    def get(self, request, param: int = Query(10, const=True)):
        print(param, type(param))
        return HttpResponse(param)

    # If your parameter is of numeric type , you can use `ge`、`gt`、`le`、`lt`、`multipleOf` and other attributes
    def get(self, request,
            param1: int = Query(gt=10),  # must be > 10
            param2: int = Query(ge=10),  # must be >= 10
            param3: int = Query(lt=10),  # must be < 10
            param4: int = Query(le=10),  # must be <= 10
            param5: int = Query(multipleOf=10),  # must be a multiple of 10
        ):
        return HttpResponse(param)
```

And there are more attributes applied to `str` or `list` type, you can refer to the following table:

#### All properties and description
| Name           | description |
| ---            | ---         |
| default        | since this is replacing the field’s default, its first argument is used to set the default, do not pass `default` or `default_factory` to indicate that this is a required field
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



## More
When you finish the above tutorial, you can already declare parameters well. 
Next, you can use the functions of "parameter verification" and "document generation".

Click [Parameter Verification](parameter-verification.md) to see how to verify parameters.

Click [Document Generation](document-generation.md) to see how to Generating documentation.

