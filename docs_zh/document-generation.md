**提示：**
如果要自动生成接口文档，必须将 `django-simple-api` 的 url 添加到你的根 urls.py 中，参考 [快速入门](quick-start.md)。

## 修改接口文档描述信息
你可以在添加 url 的地方修改接口文档中的描述信息，如下：

```python
# urls.py

from django.urls import include, path
from django.conf import settings


# 根 urls
urlpatterns = [
    ...
]

# dsa 的 urls, 应该只在测试环境运行！
if settings.DEBUG:
    urlpatterns += [
        # # 接口文档 url
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

在上面的例子中，你可以修改 `template_name` 来改变界面文档的 UI 主题，我们目前有两个 UI 主题：swagger.html 和 redoc.html。

然后你可以通过 `title`、`description` 和 `version` 来修改接口文档的标题、描述和版本。


## 使用函数视图生成接口文档
如果你正在使用的是类视图，那你不需要这一步，你可以直接启动服务，查看接口文档了。

但是如果使用函数视图，则必须声明函数视图支持的请求方法：
```python
# views.py

from django_simple_api import allow_request_method

@allow_request_method("get")
def just_test(request, id: int = Query()):
    return HttpResponse(id)
```

`allow_request_method` 只能声明一种请求方法,并且必须是 `['get', 'post', 'put', 'patch', 'delete', 'head', 'options', trace']` 中的一种。

同一个视图函数不支持多次使用 `allow_request_method`，每个请求方法应该有一个单独的视图函数来支持，否则我们无法知晓这个视图函数的参数，是用于 `get` 方法还是 `post` 方法。

注意，如果使用 `@allow_request_method("get")`，则不能使用除 `get` 以外的请求方法，否则会返回 `405 Method Not Allow` 错误。

你也可以不使用 `allow_request_method`，这不会产生任何负面影响，只是无法生成文档。
如果你没有在函数视图上使用 `allow_request_method`，我们会用 `warning.warn()` 来提醒你，这不是个问题，只是为了防止你忘记使用它。

现在，函数视图也可以生成接口文档了，你可以访问你的服务器查看效果。

## 完善接口文档信息
`django-simple-api` [`OpenAPI`](https://github.com/OAI/OpenAPI-Specification) 的规范来生成接口文档的。
除了自动生成的参数信息外，你还可以手动为每个接口添加更加详细的信息，例如 `summary`、`description `、`responses` 和 `tags`。

### 添加 `summary` 和 `description`
`summary` 用于简要介绍接口的功能，`description` 则用于详细描述接口更多的信息。

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
> **注意：** `summary` 和 `description` 和之间必须有一个空行，如果没有空行，则全部视为 `summary`。


### 添加响应信息

`responses` 也是接口文档中的重要信息，你可以定义接口在各种情况下应返回的数据格式和类型。

`django-simple-api` 强烈推荐使用 `pydantic.BaseModel` 来定义响应信息的数据结构，例如:

```python
# views.py

from typing import List

from pydantic import BaseModel
from django.views import View

from django_simple_api import describe_response


# 为 `response` 定义数据结构和类型
class JustTestResponses(BaseModel):
    code: str
    message: str
    data: List[dict]


class JustTest(View):
    # 使用 @describe_response 为接口添加响应信息
    @describe_response(200, content=JustTestResponses)
    def get(self, request, id: int = Query()):

        # 实际响应数据(仅做演示)
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

最终，接口文档会展示为：

```shell
{
  "code": "string",
  "message": "string",
  "data": [
    {}
  ]
}
```

你也可以直接在接口文档中展示'示例'，只需将'示例'添加到 `pydantic.BaseModel` 文档中即可：

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

最终接口文档会展示为：

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

`django-simple-api` 的默认响应类型是 `application/json`, 如果要设置其他类型，可以这样：

```python
# views.py

class JustTest(View):
    
    @describe_response(401, content={"text/plain":{"schema": {"type": "string", "example": "No permission"}}})
    def get(self, request, id: int = Query()):
        return JsonResponse(id)
```

虽然我们支持自定义响应类型和数据结构，但我们建议你尽量不要这样做，除非是像示例中那样非常简单的响应，
否则会在你的代码文件中占用大量空间并且不利于让团队中的其他人阅读代码。

如果你需要描述多个响应信息，那么我们会推荐使用 `describe_responses`，它可以一次描述多个响应状态，这相当于同时使用多个 `describe_response`：

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

> 如果你想添加公共的响应信息到多个接口，你可以使用：[wrapper_include](extensions-function.md#wrapper_include)


### 添加标记

`OpenAPI` 支持通过标记来对接口进行分组管理，你可以通过下面的方法来为接口添加标记:

```python
from django_simple_api import mark_tags, allow_request_method, Query

@mark_tags("about User")
@allow_request_method("get")
def get_name(request, id: int = Query(...)):
    return HttpResponse(get_name_by_id(id))
```

除此之外，你也可以使用 `@mark_tags("tag1", "tag2")` 为接口添加多个标签。

> 如果你想同时为多个接口添加标签，你可以使用：[wrapper_include](extensions-function.md#wrapper_include)
