from __future__ import annotations

from django.urls import path
from .apps import DjangoBirdAppConfig
from .views import component_detail
from .views import component_list

app_name = DjangoBirdAppConfig.label

urlpatterns = [
    path("components/", component_list, name="component-list"),
    path("components/<str:component_name>/", component_detail, name="component-detail"),
]
