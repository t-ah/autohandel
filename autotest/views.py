from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


def index(_):
    return HttpResponse("<a href=\"admin\">Weiter zur App</a>")

@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True) # one day
def favicon(_: HttpRequest):
    file = (settings.BASE_DIR / "static" / "favicon.png").open("rb")
    return FileResponse(file)