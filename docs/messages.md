# Messages

Quite commonly in web applications, you need to display a one-time notification message (also known as “flash message”) to the user after processing a form or some other type of user input.

For this, Django provides full support for session-based messaging, including both anonymous and authenticated users. The messages framework allows you to temporarily store messages in one request and retrieve them for display in a subsequent request (usually the next one). Every message is tagged with a specific category (e.g., **info**, **warning**, or **error**) this can be used as a class name to style the message.

A message can be used in the context of a request, for example:

```python
from starlette_core.messages import message

async def post(self, request):
    # handle post request
    message(request, "WooHoo You're Home", "success")
    # return the response (ie a RedirectResponse)
```

!!! warning "Template function"

    To use the `get_messages()` within a template, your templates will need to be loaded
    via our `Jinja2Templates` loader.
    [See docs](/templating).

```html
<ul class="messages">
{% for message in get_messages() %}
    <li class="message-{{ message.catagory }}">{{ message.message }}</li>
{% endfor %}
</ul>
```