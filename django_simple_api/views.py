import operator
import warnings
from copy import deepcopy
from functools import reduce
from typing import Any, Dict, Tuple

from django.http.response import JsonResponse
from django.shortcuts import render

from .exceptions import RequestValidationError
from .extras import merge_openapi_info
from .schema import schema_parameter, schema_request_body, schema_response
from .utils import get_all_urls, is_class_view


def docs(request, template_name: str = "swagger.html", **kwargs: Any):
    return render(request, template_name, context={})


def _generate_method_docs(function) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    result: Dict[str, Any] = {}
    definitions: Dict[str, Any] = {}

    doc = function.__doc__
    if isinstance(doc, str):
        clean_doc = "\n".join(i.strip() for i in doc.strip().splitlines())
        result.update(zip(("summary", "description"), clean_doc.split("\n\n", 1)))

    # generate params schema
    parameters = reduce(
        operator.add,
        [
            schema_parameter(getattr(function, "__parameters__", {}).get(key), key)
            for key in ["path", "query", "header", "cookie"]
        ],
    )
    result["parameters"] = parameters

    # generate request body schema
    request_body, _definitions = schema_request_body(
        getattr(function, "__request_body__", None)
    )
    result["requestBody"] = request_body
    definitions.update(_definitions)

    # generate responses schema
    __responses__ = getattr(function, "__responses__", {})
    responses: Dict[int, Any] = {}
    if parameters or request_body:
        responses[422] = {
            "content": {
                "application/json": {"schema": RequestValidationError.schema()}
            },
            "description": "Failed to verify request parameters",
        }

    for status, info in __responses__.items():
        _ = responses[int(status)] = dict(info)
        if _.get("content") is not None:
            _["content"], _definitions = schema_response(_["content"])
            definitions.update(_definitions)

    result["responses"] = responses

    # merge user custom operation info
    return (
        merge_openapi_info(
            {k: v for k, v in result.items() if v},
            getattr(function, "__extra_docs__", {}),
        ),
        definitions,
    )


def _generate_path_docs(handler) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    result: Dict[str, Any] = {}
    definitions: Dict[str, Any] = {}
    if is_class_view(handler):
        view_class = handler.view_class
        for method in filter(
            lambda method: hasattr(view_class, method) and method not in ("options",),
            view_class.http_method_names,
        ):
            result[method], _definitions = _generate_method_docs(
                getattr(view_class, method)
            )
            definitions.update(_definitions)
    else:
        if hasattr(handler, "__method__"):
            result[handler.__method__.lower()], _definitions = _generate_method_docs(
                handler
            )
            definitions.update(_definitions)
        elif (
            hasattr(handler, "__parameters__")
            or hasattr(handler, "__request_body__")
            or hasattr(handler, "__responses__")
        ):
            warnings.warn(
                "You used the type identifier but did not declare the "
                f"request method allowed by the function {handler.__qualname__}. We cannot "
                "generate the OpenAPI document of this function for you!"
            )
    return {k: v for k, v in result.items() if v}, definitions


def get_docs(
    request,
    title: str = "Django Simple API",
    description: str = "This is description of your API document.",
    version: str = "0.1.0",
    **kwargs: Any,
):

    openapi_docs = {
        "openapi": "3.0.0",
        "info": {"title": title, "description": description, "version": version},
        "servers": [
            {
                "url": request.build_absolute_uri("/"),
                "description": "Current API Server Host",
            },
            {
                "url": "{schema}://{address}/",
                "description": "Custom API Server Host",
                "variables": {
                    "schema": {
                        "default": request.scheme,
                        "description": "http or https",
                    },
                    "address": {
                        "default": request.get_host(),
                        "description": "api server's host[:port]",
                    },
                },
            },
        ],
    }
    definitions = {}
    paths = {}
    for url_pattern, view in get_all_urls():
        paths[url_pattern], _definitions = _generate_path_docs(view)
        definitions.update(_definitions)
    openapi_docs["paths"] = {k: v for k, v in paths.items() if v}
    openapi_docs["definitions"] = deepcopy(definitions)
    return JsonResponse(openapi_docs, json_dumps_params={"ensure_ascii": False})
