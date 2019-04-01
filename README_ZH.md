# Django Simple Api

一个用于快速创建简单Api的非侵入式Django组件

## 如何使用

1. 将`'django_simple_api'` 加入 `INSTALLED_APPS`

2. 将 `'django_simple_api.middleware.RequestParsingMiddleware'` 加入 `MIDDLEWARE`

然后你就可以愉快的使用了

```python
from django_simple_api.views import SimpleApiView
from django_simple_api.response import jsonify

class ReplyApiView(SimpleApiView):
    def get(self, request):
        return jsonify(request.JSON)
```
