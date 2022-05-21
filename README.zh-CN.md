Language: [English](README.md) | Chinese

# Django Simple API
***Django Simple API*** 是基于 Django 的一个非侵入式组件，可以帮助您快速创建 API。

## 快速开始

### 安装

从 github 下载并安装：

```shell
pip install django-simple-api
```

### 配置

第一步：将 `django-simple-api` 添加到 `settings.INSTALLED_APPS` 中：

```python
INSTALLED_APPS = [
    ...,
    "django_simple_api",
]
```

第二步：将中间件注册到 `settings.MIDDLEWARE` 中：

```python
MIDDLEWARE = [
    ...,
    "django_simple_api.middleware.SimpleApiMiddleware",
]
```

第三步：将 `django-simple-api` 的 url 添加到根 urls.py 中：

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
        # 接口文档 url
        path("docs/", include("django_simple_api.urls"))
    ]
```

### 完成第一个示例

首先，定义一个路由:

```python
# your urls.py

from django.urls import path
from yourviews import JustTest

urlpatterns = [
    ...,
    path("/path/<int:id>/", JustTest.as_view()),
]
```

然后定义一个视图:

```python
# your views.py

from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Query


class JustTest(View):
    def get(self, request, id: int = Query()):
        return HttpResponse(id)
```
> ⚠️ 注意：要生成文档，必须使用 `django-simple-api`  的规则声明参数(如上图所示)！
>
> 点击 [声明参数](declare-parameters.md) 查看如何声明参数。

### 访问接口文档

完成上述配置和示例后，现在就可以启动服务器并访问接口文档了。

如果你的服务在本地运行，可以访问 [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/) 来查看接口文档。

## More

更多详细教程, 请查看 [Django Simple API](https://django-simple-api.aber.sh/).
