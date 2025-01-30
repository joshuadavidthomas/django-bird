from __future__ import annotations

import pytest
from django.template.engine import Engine

from django_bird.loader import BirdLoader


def test_bird_loader_deprecation_warning():
    with pytest.warns(
        DeprecationWarning,
        match=(
            "BirdLoader is deprecated and will be removed in a future version. "
            "Please remove 'django_bird.loader.BirdLoader' from your TEMPLATES setting "
            "in settings.py and use Django's built-in 'django.template.loaders.filesystem.Loader' instead."
        ),
    ):
        BirdLoader(Engine())
