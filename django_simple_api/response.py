from django.http import JsonResponse


def jsonify(body=None, *, status: int = 200, **kwargs):
    """
    :param body: 如果不是None, 则只将此参数作为回复内容。
    :param status: HTTP状态码, 详见 https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status
    :param kwargs: 将被转为字典作为返回内容
    :return:
    """
    if body is None:
        return JsonResponse(kwargs, status=status)
    return JsonResponse(body, status=status, safe=False)
