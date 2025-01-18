from __future__ import annotations

import warnings

from django.conf import settings
from django.http import FileResponse
from django.http import Http404
from django.http.request import HttpRequest
from django.template.exceptions import TemplateDoesNotExist

from .components import components


def asset_view(request: HttpRequest, component_name: str, asset_filename: str):
    if not settings.DEBUG:
        warnings.warn(
            "Serving assets through this view in production is not recommended.",
            RuntimeWarning,
            stacklevel=2,
        )

    try:
        component = components.get_component(component_name)
    except (KeyError, TemplateDoesNotExist) as err:
        raise Http404("Component not found") from err

    asset = component.get_asset(asset_filename)
    if not asset or not asset.path.exists():
        raise Http404("Asset not found")

    with open(asset.path, "rb") as f:
        content = f.read()

    return FileResponse(content, content_type=asset.type.content_type)