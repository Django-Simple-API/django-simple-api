## wrapper_include

`wrapper_include` 可以批量的在视图上使用装饰器，你可以用它来批量应用 `@describe_responses`，`@mark_tags` 等装饰器。

```python
from django_simple_api import wrapper_include, mark_tags

urlpatterns = [
    ...,
    # 批量添加标签
    path("app/", wrapper_include([mark_tags("demo tag")], include("app.urls"))),
    # 批量添加响应信息
    path("app/", wrapper_include([describe_response(200, "ok")], include("app.urls"))),
    # 或者可以同时使用
    path("app/", wrapper_include([mark_tags("demo tag"), describe_response(200, "ok")], include("app.urls"))),
]
```

## Support for JSON requests

## To be continue ...
