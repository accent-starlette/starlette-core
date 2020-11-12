from starlette.authentication import requires
from starlette.responses import PlainTextResponse

from .models import DemoModel


@requires('authenticated')
async def homepage(request):
    ct = await DemoModel.get_or_404(1)
    return PlainTextResponse(f"DemoModel = {ct}")
