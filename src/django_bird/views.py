from __future__ import annotations

import warnings
from io import BytesIO

from django.conf import settings
from django.http import FileResponse
from django.http import Http404
from django.http.request import HttpRequest
from django.template.exceptions import TemplateDoesNotExist

from .components import components


def asset_view(request: HttpRequest, component_name: str, asset_filename: str):
    warnings.warn(
        "The 'asset_view' is deprecated and will be removed in a future release. "
        "Use the 'BirdAssetFinder' with Django's static files system instead.",
        DeprecationWarning,
        stacklevel=2,
    )

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

    content = asset.path.read_bytes()

    return FileResponse(BytesIO(content), content_type=asset.type.content_type)
