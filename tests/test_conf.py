from __future__ import annotations

import pytest

from django_bird.conf import app_settings


def test_app_settings():
    # stub test until `bird` requires custom app settings
    with pytest.raises(AttributeError):
        assert app_settings.foo
