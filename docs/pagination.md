# Pagination

With starlette-core we include a global `Paginator` class for the project.

This will support splitting data across multiple pages, auto-generating page numbers and calling a page via it's numerator. Allowing the use of **“Previous/Next”** links in a template.

By passing Paginator a list of objects, plus the number of items you’d like to have on each page, it provides you with methods for accessing the items for each page:

```python
from starlette_core.paginator import Paginator

# paginate objects with 25 items per page
paginator = Paginator(objects, 25)
# total records in all pages
paginator.count
# total pages in paginator
paginator.num_pages

# get page 1
page = paginator.page(1)
# get the list of objects in that page
page.object_list
# get the page number
page.number
# are there any other pages
page.has_other_pages
# is there a previous page
page.has_previous
# get previous page number
page.previous_page_number
# is there a next page
page.has_previous
# get next page number
page.next_page_number
```

## Template Implementation

We pass Paginator into a template using the request method. This example assumes you have a Users model that has already been imported:


```Python
from starlette_core.paginator import Paginator

async def listing(request):
    user_list = Users.objects.all()
    paginator = Paginator(user_list, 25) # Show 25 contacts per page

    page_number = request.query_params.get("page", 1)
    page = paginator.get_page(page_number)

    template = "list.html"
    context = {"request": request, "paginator": paginator, "page": page}
    return templates.TemplateResponse(template, context)
```

In the template you will want to be able to navigate between pages. This can be achieved by referencing `paginator` and `page`:

```html
<div>
{% if page.has_previous %}
    <a class="button" href="?page=1">First</a>
    <a class="button" href="?page={{ page.previous_page_number }}">Previous</a>
{% endif %}
</div>
<div>Page {{ page.number }} of {{ paginator.num_pages }} - {{ paginator.count }} record{% if paginator.count != 1 %}s{% endif %}</div>
<div>
{% if page.has_next %}
    <a class="button" href="?page={{ page.next_page_number }}">Next</a>
    <a class="button" href="?page={{ paginator.num_pages }}">Last</a>
{% endif %}
</div>
```