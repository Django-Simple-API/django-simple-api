参数声明是 `django-simple-api` 的基础。无论是自动验证请求参数，还是自动生成接口文档，
都必须先学会如何声明参数。

你可以像下方示例一样声明参数：

```python
# views.py

from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Query

class JustTest(View):
    def get(self, request, 
            # `id` 是参数名称
            # `int` 是参数类型
            # `Query` 表示参数所在的位置，并且可以描述有关参数的各种信息
            id: int = Query()
        ):
        return HttpResponse(id)
```


## 字段
`django-simple-api` 总共有 5 种字段，分别代表不同位置的参数：

**全部字段及其描述：**

| Field     | Description |
| ---       | ---         |
| Query     | 表示此参数为 url 查询参数，example: http://host/?param=1|
| Path      | 表示此参数为 url 路径参数，example: http://host/{param}/|
| Body      | 表示此参数在 body 中，注意：此时该参数只能在非 GET 请求中获取|
| Cookie    | 表示此参数在 Cookie 中获取|
| Header    | 表示此参数在 Header 中获取|


**示例：**
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
    # 以下示例中使用的参数名称仅用于演示。
    def post(self, request,
            # param1 将会从查询字符串中获取
            param1: int = Query(),
             
            # param2 param3 将从 url 路径中获取
            # 可以多次使用来获取多个参数
            param2: int = Path(),
            param3: str = Path(),
             
            # param4 将从 body 中获取
            param4: str = Body(),
            
            # userid username 将从 Cookie 中获取
            # alias 表示将从 Cookie 获取名为 uid 的参数，然后赋值给 userid
            userid: int = Cookie(alias="uid"),
            username: int = Cookie(alias="user_name"),
            
            # token 将从 Header 中获取
            csrf_token: str = Header(alias="X-Csrf-Token"),
        ):

        return HttpResponse(username)
```

> ⚠️ 注意：当需要从 Header 中获取参数时，可能需要使用 alias 来指明要获取的请求头，因为请求头的名称可能不是有效的 Python 标识符。


## 字段属性
默认情况下，使用字段声明的参数，都是必填参数。如下个例子中，如果 url 中没有 `id` 参数，则会返回一个客户端错误：
```python
class JustTest(View):
    def get(self, request, id: int = Query()):
        return HttpResponse(id)
```

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

### 非必填和默认参数
如果你想将参数设置为非必填，或者设置一个默认值，则可以使用以下方法：
```python
# views.py

class JustTest(View):
    def get(self, request, 
            # 参数 name 为非必填
            name: str = Query(None),
            
            # 参数 id 默认值为 10
            id: int = Query(default=10)
            ):
        return HttpResponse(id)
```

或者你可以使用 `default_factory` 传入一个函数来动态计算默认值：

```python
# views.py

def func():
    return 1000

class JustTest(View):
    def get(self, request, id: int = Query(default_factory=func)):
        print(id)  # 1000
        return HttpResponse(id)
```

> ⚠️ 注意：不能同时使用 `default` 和 `default_factory`，否则会报错 `ValueError: cannot specify both default and default_factory`。

### 其他的字段属性
| Name           | description |
| ---            | ---         |
| default        | 参数的默认值 |
| default_factory| 生成参数默认值的可调用对象，`default_factory` 和 `default` 不可同时使用 |
| alias          | 别名，从目标位置获取参数的真正名字，接口文档也会展示此名字，默认同参数名 |
| title          | 任意字符串 |
| description    | 参数描述，将会展示在接口文档中 |
| exclusive      | 独占模式，使用该模式时，必须定义一个 `pydantic.BaseModel` 的子类作为表单，一次性接受所有参数；点击 [查看示例](#独占模式) |


#### 独占模式
`exclusive` 是一个特殊的属性，当你有一整个表单需要提交时，可以使用独占模式。

首先使用 `pydantic.BaseModel` 来定义一个数据模型，然后使用数据模型从指定字段（`Query`、`Body`）中一次性接收所有同字段类型参数：
```python
# views.py

from django.views import View
from pydantic import BaseModel, Field

from django_simple_api import Body


# 使用 `pydantic.BaseModel` 来定义一个数据模型
class UserForm(BaseModel):
    name: str = Field(max_length=25, description="This is user's name")
    age: int = Field(19, description="This is user's age")


class UserView(View):
    def post(self, request, 
            # 使用 `exclusive=True` 从 Body 中一次性获取所有参数:
            user: UserForm = Body(exclusive=True)
        ):

        # 然后可以从数据模型中获取参数
        name = user.name
        age = user.age
        
        # 也可以将其转换成字典:
        user.dict()  # {"name": ..., "age": ...}
        
        # 更多数据模型的用法，请查看 https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict
        
        return HttpResponse("success")
```
> ⚠️ 注意，当使用独占模式时，你不能再在同一个接口中使用相同的字段，但不影响其他字段的使用。
> 例如上述示例中使用了 `user: UserForm = Body(exclusive=True)`，那么就不能再使用 `id:int = Body()` 来声明参数，因为 Body 中所有的参数，都会聚合到 `user` 中。
> 但是你可以使用其他的字段类型，如 `Query` `Path` 等。


## 类型转换
`django-simple-api` 还具有类型转换的功能。如果你传入的参数对于声明的类型是合法的，它会被自动转换为声明的类型，无需手动操作：

```python
# views.py

class JustTest(View):
    def get(self, request, 
            # 接收到的是个日期字符串，会被直接转成 date 类型
            last_time: datetime.date = Query()
            ):
        
        # 2008-08-08 <class 'datetime.date'>
        print(last_time, type(last_time))
        
        return HttpResponse(last_time)
```


## 约束请求参数

> `django-simple-api` 利用 `pydantic` 来对请求参数做出限制，每种类型的参数拥有不同的限制，下方示例中展示了常用的参数类型及其限制条件，
> 更多教程请查阅 [Pydantic](https://pydantic-docs.helpmanual.io/usage/models/)。

```python
# views.py
from django.views import View
from pydantic import conint, confloat, constr, conlist
from django_simple_api import Query, Body

class JustTest(View):

    # 数值类型，可以使用 ge、gt、le、lt、multipleOf 等限制条件。
    def get(self, request,
            p1: conint(gt=10) = Query(),  # 必须 > 10
            p2: conint(ge=10) = Query(),  # 必须 >= 10
            p3: confloat(lt=10.5) = Query(),  # 必须 < 10.5
            p4: confloat(le=10.5) = Query(),  # 必须 <= 10.5
            p5: conint(multiple_of=10) = Query(),  # 必须是 10 的倍数
        ):
        return HttpResponse("Success")

    # 字符串类型, 可以使用 strip_whitespace、to_lower、max_length、min_length、curtail_length、regex 等限制条件。
    def get(self, request,
            p1: constr(strip_whitespace=True) = Query(),  # 去掉两边的空白字符
            p2: constr(to_lower=True) = Query(),  # 将字符串转换为小写
            p3: constr(max_length=20) = Query(),  # 字符串的最大长度不能超过 20
            p4: constr(min_length=8) = Query(),  # 字符串的最小长度不能小于 8
            p5: constr(curtail_length=10) = Query(),  # 截取字符串前 10 个字符
            p6: constr(regex='/^(?:(?:\+|00)86)?1[3-9]\d{9}$/') = Query(),  # 字符串是否符合正则表达式
    ):
        return HttpResponse("Success")
    
    # 列表类型，可以使用 item_type、max_items、min_items 等限制条件。
    def post(self, request,
            p1: conlist(item_type=int, min_items=1) = Body(),  # 列表中至少有 1 个元素，并且应为 int 类型。
            p2: conlist(item_type=str, max_items=5) = Body(),  # 列表中最多有 5 个元素，并且应为 str 类型。
    ):
        return HttpResponse("Success")
```


## 更多
完成上述教程后，你应该明白怎么声明参数了。接下来就可以使用 **参数校验** 和 **生成接口文档** 的功能了。

点击 [参数校验](parameter-verification.md) 查看如何自动校验请求参数。

点击 [生成文档](document-generation.md) 查看如何自动生成接口文档。
