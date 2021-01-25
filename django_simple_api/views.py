import warnings

from django.conf import settings
from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import JsonResponse

from .utils import get_urls, is_class_view
from .decorators import allow_method


@allow_method("get")
def docs(request: HttpRequest):
    theme_name = (
        settings.SIMPLE_API_THEME if settings.SIMPLE_API_THEME else "swagger.html"
    )
    return render(request, theme_name, context={})


@allow_method("get")
def get_docs(request: HttpRequest):
    # default_request_type = ["application/json", "multipart/form-data"]
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Django Simple API",
            "version": "1.0.0",
            "description": "This is a simple API",
        },
        "servers": [{"description": "Server Host", "url": request.get_host()}],
        "tags": [],
        "paths": {
            "/inventory": {
                "get": {
                    "tags": ["developers"],
                    "summary": "searches inventory",
                    "operationId": "searchInventory",
                    "description": "By passing in the appropriate options, you can search for\navailable inventory in the system\n",
                    "parameters": [
                        {
                            "in": "query",
                            "name": "searchString",
                            "description": "pass an optional search string for looking up inventory",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                        {
                            "in": "query",
                            "name": "skip",
                            "description": "number of records to skip for pagination",
                            "schema": {
                                "type": "integer",
                                "format": "int32",
                                "minimum": 0,
                            },
                        },
                        {
                            "in": "query",
                            "name": "limit",
                            "description": "maximum number of records to return",
                            "schema": {
                                "type": "integer",
                                "format": "int32",
                                "minimum": 0,
                                "maximum": 50,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "search results matching criteria",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/InventoryItem"
                                        },
                                    }
                                }
                            },
                        },
                        "400": {"description": "bad input parameter"},
                    },
                },
                "post": {
                    "summary": "adds an inventory item",
                    "operationId": "addInventory",
                    "description": "Adds an item to the system",
                    "responses": {
                        "201": {"description": "item created"},
                        "400": {"description": "invalid input, object invalid"},
                        "409": {"description": "an existing item already exists"},
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InventoryItem"}
                            }
                        },
                        "description": "Inventory item to add",
                    },
                },
            }
        },
    }
    for url_pattern, view in get_urls():
        path_info = {}

        # 忽略部分 url
        if url_pattern in ["docs/", "docs/get_docs/"]:
            continue

        if is_class_view(view):
            view_class = view.view_class
            for method in view_class.http_method_names:
                if hasattr(view_class, method):
                    handler = getattr(view_class, method)
                    # todo 抽出来
                    summary = (
                        handler.__doc__.split("\n\n")[0].strip()
                        if handler.__doc__ is not None
                        else ""
                    )
                    description = (
                        handler.__doc__.split("\n\n")[-1].strip()
                        if handler.__doc__ is not None
                        else ""
                    )
                    # todo 获取请求参数
                    # todo 获取响应参数
                    # 单个请求方法
                    path_info[method] = {
                        "summary": summary,
                        "description": description,
                        "parameters": [],
                        "": {},
                    }
        else:
            request_method = getattr(view, "__method__", None)
            if not request_method:
                warnings.warn(
                    f"`{view.__name__}` view function does not declare request method, "
                    f"we cannot generate documentation for it!"
                )
            else:
                pass

        # 合并到 openapi
        # openapi["paths"][url_pattern] = path_info

    return JsonResponse(openapi, json_dumps_params={"ensure_ascii": False})
