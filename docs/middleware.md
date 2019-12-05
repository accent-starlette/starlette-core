# Middleware

There are some useful middleware included you can use as described below.

## `DatabaseMiddleware`

Because we use sessions in starlette-core, by default `Sessions` are defined globally. This means
when you do a `Session.commit()` or `Session.rollback()` this can bleed accross active requests.

This middleware provides a `scopefunc` to the `Session` that isolates the session to a single 
request. [See docs](https://docs.sqlalchemy.org/en/13/orm/contextual.html#using-custom-created-scopes).


!!! warning "Using the `DatabaseMiddleware`"

    If you are using the database functionality provided by this package it is important to use this middleware.
    [See docs](/database).

Enable the middleware:

```python
from starlette_core.middleware import DatabaseMiddleware

app.add_middleware(DatabaseMiddleware)
```

## `CurrentRequestMiddleware`

This middleware provides a useful function to get the current request object.
This enables modules to access the likes of the current logged in user outside of the view/endpoint.

Enable the middleware:

```python
from starlette_core.middleware import CurrentRequestMiddleware

app.add_middleware(CurrentRequestMiddleware)
```

Access the request object:

```python
from starlette_core.middleware import get_request

request = get_request()
if request:
    user = request.get("user")
```