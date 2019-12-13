# Templating

At the time of publication, Starlette's [templates](https://www.starlette.io/templates/) only supports
passing in a directory to load templates from. Since we have multiple repos that can
all include their own templates, we have provided a modified version which takes in a Jinja2 [loader](https://jinja.palletsprojects.com/en/2.10.x/api/#loaders) as its argument.

This allows for more complex scenarios such as referencing multiple directories and those outside of the current project, for example:


```python
import jinja2
from starlette_core.templating import Jinja2Templates

templates = Jinja2Templates(
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.PackageLoader("starlette_admin", "templates"),
        ]
    )
)

async def home(self, request):
    template = "home.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)
```

## Jinja2 Extensions

[Extensions](https://jinja.palletsprojects.com/en/2.10.x/extensions/) can be added by providing 
configuration to this package.

[See docs](/configuration).
