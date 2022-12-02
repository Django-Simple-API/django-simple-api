# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_simple_api']

package_data = \
{'': ['*'], 'django_simple_api': ['static/*', 'templates/*']}

install_requires = \
['Pillow>=8.2,<10.0', 'django', 'pydantic>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'django-simple-api',
    'version': '0.1.0',
    'description': 'A non-intrusive component that can help you quickly create APIs.',
    'long_description': '**Language: English | [Chinese](README.zh-CN.md)**\n\n# Django Simple API\n\nA non-intrusive component that can help you quickly create APIs.\n\n## Quick Start\n\n### Install\n\nDownload and install from github:\n\n```\npip install django-simple-api\n```\n\n### Configure\n\nAdd django-simple-api to your `INSTALLED_APPS` in settings:\n\n```python\nINSTALLED_APPS = [\n    ...,\n    "django_simple_api",\n]\n```\n\nRegister the middleware to your `MIDDLEWARE` in settings:\n\n```python\nMIDDLEWARE = [\n    ...,\n    "django_simple_api.middleware.SimpleApiMiddleware",\n]\n```\n\nAdd the url of ***django-simple-api*** to your urls.py:\n\n```python\n# urls.py\n\nfrom django.urls import include, path\nfrom django.conf import settings\n\n# Your urls\nurlpatterns = [\n    ...\n]\n\n# Simple API urls, should only run in a test environment.\nif settings.DEBUG:\n    urlpatterns += [\n        # generate documentation\n        path("docs/", include("django_simple_api.urls"))\n    ]\n```\n\n### Complete the first example\n\nDefine your url:\n\n```python\n# your urls.py\n\nfrom django.urls import path\nfrom yourviews import JustTest\n\nurlpatterns = [\n    ...,\n    path("/path/<int:id>/", JustTest.as_view()),\n]\n```\n\nDefine your view:\n\n```python\n# your views.py\n\nfrom django.views import View\nfrom django.http.response import HttpResponse\n\nfrom django_simple_api import Query\n\n\nclass JustTest(View):\n    def get(self, request, id: int = Query()):\n        return HttpResponse(id)\n```\n\n> ⚠️ To generate the document, you must declare the parameters according to the  rules of ***Simple API*** (like the example above).\n>\n> Click [Declare parameters](https://django-simple-api.aber.sh/declare-parameters/) to see how to declare parameters.\n\n### Access interface document\n\nAfter the above configuration, you can start your server and access the interface documentation now.\n\nIf your service is running locally, you can visit [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/) to view\nyour documentation.\n\n## More\n\nFor more tutorials, see [Django Simple API](https://django-simple-api.aber.sh/).\n',
    'author': 'abersheeran',
    'author_email': 'me@abersheeran.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/abersheeran/django-simple-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

