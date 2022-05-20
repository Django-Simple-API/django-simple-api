**提示：**
不要忘记配置 `INSTALLED_APPS` 和 `MIDDLEWARE `，点击 [快速开始](quick-start.md) 学习如何配置。


**自动校验请求参数**是默认开启的功能，当你使用[字段](declare-parameters.md#字段)声明参数时，`django-simple-api` 会自动检查参数是否合法。

如果您的请求参数校验失败，则会返回一个 `422` 客户端错误，如下图所示：
```shell
[
    {
        "loc": [
            "id"
        ],
        "msg": "value is not a valid integer",
        "type": "type_error.integer"
    }
]
```

在上面的错误信息中，`loc` 指出了哪个参数有错误，`msg` 描述了错误的原因。有了这些信息，便可以快速定位参数问题了。
