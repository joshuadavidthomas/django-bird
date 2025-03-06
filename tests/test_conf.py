from __future__ import annotations

import pytest
from django.test import override_settings

from django_bird.conf import app_settings


@pytest.mark.default_app_settings
def test_app_settings():
    assert app_settings.COMPONENT_DIRS == []
    assert app_settings.ENABLE_BIRD_ATTRS is True


def test_component_directory_names():
    assert app_settings.get_component_directory_names() == ["bird"]

    with override_settings(DJANGO_BIRD={"COMPONENT_DIRS": ["components"]}):
        assert app_settings.get_component_directory_names() == ["components", "bird"]
