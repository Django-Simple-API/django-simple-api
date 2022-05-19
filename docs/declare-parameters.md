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
### All fields and description
| Field     | Description |
| ---       | ---         |
| Query     | Indicates that this parameter is in the url query string. example: http://host/?param=1|
| Path      | Indicates that this parameter is a url path parameter. example: http://host/{param}/|
| Body      | Indicates that this parameter is in the request body, and the value can only be obtained in a non-GET request.|
| Cookie    | Indicates that this parameter is in Cookie.|
| Header    | Indicates that this parameter is in Header.|

### For example:

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
            csrf_token: str = Header(alias="X-Csrf-Token"),
        ):

        return HttpResponse(username)
```

> ⚠️ In the above example, you have two things to note:
>
> * If you have more than one parameter in a field, you can use the field multiple times to describe different parameters.
> * When you need to get parameters from `Header`, you may need to use `alias` to indicate the request header you want to get, because the name of the request header may not be a valid python identifier.


## Type conversion
***Simple API*** also has the function of type conversion. If the parameter you pass in is legal for the declared type, it will be converted to the declared type without manual operation:

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

In addition to the `default`、`default_factory`, you can also use more attributes, such as:

#### All properties and description
| Name           | description |
| ---            | ---         |
| exclusive      | Exclusive mode, when you use this mode, you must take a subclass of `pydantic.BaseModel` as a form and get all the parameters declared in the form at once. [See the sample](#Use exclusive model)|
| default        | Since this is replacing the field’s default, its first argument is used to set the default, do not pass `default` or `default_factory` to indicate that this is a required field.|
| default_factory| Callable that will be called when a default value is needed for this field. If both `default` and `default_factory` are set, an error is raised.|
| alias          | The public name of the field.|
| title          | Can be any string, used in the schema.|
| description    | Can be any string, used in the schema.|
| **extra        | Any additional keyword arguments will be added as is to the schema.|


#### Use exclusive model
`exclusive` is a special property that allows you to retrieve the entire form's parameters at once.

Example:

You can use `pydantic.BaseModel` to define a `"Form"`，
Then use the `exclusive` property to get all parameters required for `"Form"` from the `body`:


```python
# views.py

from django.views import View
from pydantic import BaseModel, Field

from django_simple_api import Body


# Use `pydantic.BaseModel` to define a `"Form"`
class UserForm(BaseModel):
    name: str = Field(max_length=25, description="This is user's name")
    age: int = Field(19, description="This is user's age")


class UserView(View):
    def post(self, request, 
            # Use the `exclusive=True` to get all parameters required for `"Form"` from the `body`:
            user: UserForm = Body(exclusive=True)
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
> ⚠️ Note, when you use `Body(exclusive=True)`, you can no longer use the `Body()` field in this view, but use of other fields will not be affected.

>There are other uses of `BaseModel`, see [`pydantic`](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict) for more details.


## Constraint request parameters
```python
# views.py
from django.views import View

from pydantic import conint,confloat, constr, conlist

from django_simple_api import Query, Body

class JustTest(View):

    # If your parameter is of numeric type , you can use `ge`、`gt`、`le`、`lt`、`multipleOf` and other attributes
    def get(self, request,
            p1: conint(gt=10) = Query(),  # must be > 10
            p2: conint(ge=10) = Query(),  # must be >= 10
            p3: confloat(lt=10.5) = Query(),  # must be < 10.5
            p4: confloat(le=10.5) = Query(),  # must be <= 10.5
            p5: conint(multiple_of=10) = Query(),  # must be a multiple of 10
        ):
        return HttpResponse("Success")

    # Or if your parameter is of str type , you can use `strip_whitespace`、`to_lower`、`max_length`、`min_length`、`curtail_length` and other attributes
    def get(self, request,
            p1: constr(strip_whitespace=True) = Query(),  # Remove blank characters on both sides.
            p2: constr(to_lower=True) = Query(),  # Convert string to lowercase
            p3: constr(max_length=20) = Query(),  # The maximum length of the string cannot exceed 20.
            p4: constr(min_length=8) = Query(),  # The minimum length of the string cannot be less than 8.
            p5: constr(curtail_length=10) = Query(),  # Intercept the first 10 characters.
    ):
        return HttpResponse("Success")

    # Or if your parameter is of list type , you can use `item_type`、`max_items`、`min_items` attributes
    def post(self, request,
            p1: conlist(item_type=int, min_items=1) = Body(),  # At least one item in the list and should be of type int.
            p2: conlist(item_type=str, max_items=5) = Body(),  # There are at most five items in the list, and they should be of type str.
    ):
        return HttpResponse("Success")
```
> For more information on attribute constraints, see [Pydantic](https://pydantic-docs.helpmanual.io/usage/models/).


## More
When you finish the above tutorial, you can already declare parameters well. 
Next, you can use the functions of "parameter verification" and "document generation".

Click [Parameter Verification](parameter-verification.md) to see how to verify parameters.

Click [Document Generation](document-generation.md) to see how to Generating documentation.

