## Install

Download and install from github

```
pip install git+https://github.com/abersheeran/django-simple-api.git@setup.py
```

Or from coding mirror in China

```
pip install git+https://e.coding.net/aber/github/django-simple-api.git@setup.py
```

Add django-simple-api to your `INSTALLED_APPS` in settings:

```python
INSTALLED_APPS = [
    ...
    "django_simple_api",
]
```

Add `SimpleApiMiddleware` to your `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    ...
    "django_simple_api.middleware.SimpleApiMiddleware",
]
```
