# Django Simple API

## 关于
***Django Simple API*** 是一个非侵入式组件，可以帮助您快速创建 API。

它不是一个类似于 DRF 的框架，它只是一个基于 Django 的轻量级插件，非常易于学习和使用。

它有 4 个核心功能：

* 自动生成接口文件(OpenAPI)
* 自动校验请求参数
* 自动支持 `application/json` 请求类型
* 为 `Model``QuerySet` 拓展序列化方法

## 学习和使用

⚠️ 此库的所有功能默认支持`函数视图`和`类视图`。如果文档中没有特别说明，则表示这两种视图都适用，如果需要特殊支持，我们会在文档中说明如何做。

[快速开始](quick-start.md)

[声明参数](declare-parameters.md)

[参数验证](parameter-verification.md)

[生成文档](document-generation.md)

[扩展功能](extensions-function.md)



