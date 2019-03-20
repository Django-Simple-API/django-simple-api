# Django Simple Api

A non-intrusive component that can help you quickly create APIs.

## How to use

1. Add `'django_simple_api'` in `INSTALLED_APPS`

2. Add `'django_simple_api.middleware.RequestParsingMiddleware'` in `MIDDLEWARE`

And then, you can use like

```python
from django_simple_api.response import jsonify

class ReplyApiView(ModelApiView):
    def get(self, request):
        return jsonify(request.JSON)
```
