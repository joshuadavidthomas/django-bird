from __future__ import annotations

from django.apps import apps

from django_bird.components import components

from .utils import TestComponent


def test_ready_scans_components(templates_dir):
    TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    TestComponent(name="alert", content="<div>Alert</div>").create(templates_dir)

    components.reset()

    assert "button" not in components._components
    assert "alert" not in components._components

    apps.get_app_config("django_bird").ready()

    assert "button" in components._components
    assert "alert" in components._components
