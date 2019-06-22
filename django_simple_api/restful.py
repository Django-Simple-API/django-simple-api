from django.http import JsonResponse


def jsonify(body=None, *, status: int, **kwargs):
    """
    :param body: 如果不是None, 则只将此参数作为回复内容。
    :param status: HTTP状态码, 详见 https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status
    :param kwargs: 将被转为字典作为返回内容
    :return:
    """
    if body is None:
        return JsonResponse(kwargs, status=status)
    return JsonResponse(body, status=status, safe=False)


def success(body=None, **kwargs):
    return jsonify(body, status=200, **kwargs)


def params_error(body=None, **kwargs):
    return jsonify(body, status=400, **kwargs)


def unauth_error(body=None, **kwargs):
    return jsonify(body, status=401, **kwargs)


def forbidden(body=None, **kwargs):
    return jsonify(body, status=403, **kwargs)


def notfound(body=None, **kwargs):
    return jsonify(body, status=404, **kwargs)


def server_error(body=None, **kwargs):
    return jsonify(body, status=500, **kwargs)
