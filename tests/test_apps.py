from __future__ import annotations

from django.apps import apps

from django_bird.components import components


def test_ready_scans_components(create_bird_template):
    create_bird_template("button", "<button>Click me</button>")
    create_bird_template("alert", "<div>Alert</div>")

    components.clear()

    assert "button" not in components._components
    assert "alert" not in components._components

    apps.get_app_config("django_bird").ready()

    assert "button" in components._components
    assert "alert" in components._components
