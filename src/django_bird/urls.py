from __future__ import annotations

import warnings
from django.urls import path

from .views import asset_view

warnings.warn(
    "Including 'django_bird.urls' is deprecated and will be removed in a future release. "
    "Use the 'BirdAssetFinder' with Django's static files system instead.",
    DeprecationWarning,
    stacklevel=2,
)

app_name = "django_bird"

urlpatterns = [
    path("assets/<str:component_name>/<str:asset_filename>", asset_view, name="asset"),
]
