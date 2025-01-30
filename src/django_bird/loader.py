from __future__ import annotations

import warnings

from django.template.engine import Engine
from django.template.loaders.filesystem import Loader as FileSystemLoader


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        warnings.warn(
            "BirdLoader is deprecated and will be removed in a future version. "
            "Please remove 'django_bird.loader.BirdLoader' from your TEMPLATES setting "
            "in settings.py and use Django's built-in 'django.template.loaders.filesystem.Loader' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(engine)
