from __future__ import annotations

import pytest

from django_bird.conf import app_settings


@pytest.mark.default_app_settings
def test_app_settings():
    assert app_settings.COMPONENT_DIRS == []
    assert app_settings.ENABLE_BIRD_ATTRS is True
    assert app_settings.DEFAULT_ONLY is False
