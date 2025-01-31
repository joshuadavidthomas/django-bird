from __future__ import annotations

import warnings
from io import BytesIO

from django.conf import settings
from django.http import FileResponse
from django.http import Http404
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist

from .components import components




from .components import components




def component_list(request: HttpRequest) -> HttpResponse:
    components.discover_components()
    return render(
        request,
        "component_list.html",
        {
            "components": sorted(
                list(components._components.values()),
                key=lambda component: component.name,
            )
        },
    )


def component_detail(request: HttpRequest, component_name: str) -> HttpResponse:
    components.discover_components()
    return render(
        request,
        "component_detail.html",
        {
            "components": sorted(
                list(components._components.values()),
                key=lambda component: component.name,
            ),
            "component": components.get_component(component_name),
        },
    )
