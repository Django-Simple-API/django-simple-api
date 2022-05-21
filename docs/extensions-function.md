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


## 支持 JSON 请求
默认情况下，Django 只支持 `application/x-www-form-urlencoded` 和 `multipart/form-data` 请求，
`django-simple-api` 扩展支持了 `application/json` 请求。点击 [Django 解析非POST请求](https://aber.sh/articles/Django-Parse-non-POST-Request/) 查看实现思路。


## 序列化方法
`django-simple-api` 还为 Django 的 `Model`、`QuerySet`、`RawQuerySet` 扩展了序列化方法，
可以让我们很方便的将 `Model`、`QuerySet` 序列化成一个字典或者列表。

**示例：**
```python
from django.views import View
from django.http.response import JsonResponse
from django.contrib.auth.models import User

from django_simple_api import Query

class SerializeDemo(View):
    
    def get(self, request, name: str=Query()):
        # 序列化 Model
        user = User.objects.get(username=name)
        # 只要使用 Model.to_json() 方法就可以将 Model 序列化出来
        user_dict = user.to_json()
        
        # 序列化 QuerySet
        users = User.objects.filter(username=name)
        # 同样只需要使用 QuerySet.to_json() 方法
        users_dict = users.to_json()
        
        return JsonResponse(data=users_dict)
```

### 隐藏敏感字段
默认情况下，使用 `to_json()` 序列化方法会将这个 `Model` 实例所有的字段全部序列化出来。
如果你不想将比较敏感的字段暴露出来，那么你可以在 `Model` 里添加一个 `buried_fields` 属性就可以隐藏敏感字段了。

**示例：**
```python
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=20)
    mobile = models.CharField(max_length=11)
    password = models.CharField(max_length=20)
    
    # 敏感字段不可暴露
    buried_fields = ['password']
```

此方式适用于在任何情况下都不会暴露出来的字段，比如用户密码，这样可以防止因某次疏忽导致账户敏感信息泄露。

> ⚠️ 注意：如果你的查询语句同时查询了关联模型，并且关联模型里也定义了 `buried_fields` 那么关联模型的敏感字段也会被隐藏。

### 排除字段
除此之外，还可以在序列化时排除不需要的字段。在调用 `to_json()` 方法时，传入 `excludes` 参数：
```python
from django.views import View
from django.http.response import JsonResponse
from django.contrib.auth.models import User

from django_simple_api import Query

class SerializeDemo(View):
    
    def get(self, request, name: str=Query()):
        user = User.objects.get(username=name)
        # 排除不需要的字段
        user_dict = user.to_json(excludes=['email', 'created_time'])
        
        # QuerySet 也同样支持
        users = User.objects.get(username=name)
        users_dict = users.to_json(excludes=['email', 'created_time'])
        
        return JsonResponse(data=user_dict)
```

> ⚠️ 注意：如果你的查询语句同时查询了关联模型，那么 `to_json()` 也会将关联模型序列化出来；
> 但是 `excludes` 只会将主模型的字段排除，而不会排除关联模型的同名字段。
> 
> 这是 `excludes` 参数与 `Model.buried_fields` 属性行为不一致的地方，请不要混淆。
