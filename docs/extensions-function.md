## wrapper_include

We also support tagging multiple URLs at the same time

```python
from django_simple_api import wrapper_include, mark_tags

urlpatterns = [
    ...,
    path("app/", wrapper_include([mark_tags("demo tag")], include("app.urls"))),
]
```

The `wrapper_include` in the above code will add `mark_tags` decorators to all views configured in the app URLs

You can also use the `wrapper_include` based functionality

```python
wrapper_include([mark_tags("demo tag"), describe_response(200, "ok")], include("app.urls"))
```

## Support for JSON requests

## To be continue ...
