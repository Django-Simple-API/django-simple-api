"Parameter verification" is enabled by default.

When you declare a parameter using "fields", 
the `Simple API` will automatically checks whether the parameter is valid in the request.


If your parameter verification fails, an error will be returned, like this:

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

In the error message above, `loc` indicates which parameter has an error, `msg` describes the cause of the error. 
With this information, you can quickly locate the problem of parameters.

**Hints:**
Don't forget to install the app and register the middleware. See [Quick Start](quick-start.md).
