from __future__ import annotations

from django.urls import path

from .apps import DjangoBirdAppConfig
from .views import asset_view

app_name = DjangoBirdAppConfig.label

urlpatterns = [
    path("assets/<str:component_name>/<str:asset_filename>", asset_view, name="asset"),
]
