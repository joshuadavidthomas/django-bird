from __future__ import annotations

import hashlib
import re
from pathlib import Path

from django.conf import settings
from django.core.cache import InvalidCacheBackendError
from django.core.cache import caches
from django.core.cache.backends.dummy import DummyCache
from django.core.cache.backends.locmem import LocMemCache
from django.template.base import Origin
from django.template.engine import Engine
from django.template.loaders.filesystem import Loader as FileSystemLoader
from django.utils.safestring import mark_safe

from ._typing import override
from .compiler import BIRD_PATTERN
from .conf import app_settings


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine, dirs: list[str | Path] | None = None) -> None:
        super().__init__(engine)
        self.templates_dir = (
            Path(dirs[0]) / "bird"
            if dirs
            else settings.TEMPLATES[0]["DIRS"][0] / "bird"
        )
        self.cache = self.get_cache()

    @override
    def get_contents(self, origin: Origin) -> str:
        contents = super().get_contents(origin)
        return self.process_bird_components(contents)

    def get_cache(self):
        for alias in [app_settings.CACHE_ALIAS, "default"]:
            try:
                backend = caches[alias]
                if not isinstance(backend, DummyCache):
                    return backend
            except InvalidCacheBackendError:
                continue

        return LocMemCache(
            name=app_settings.CACHE_ALIAS,
            params={
                "max_entries": 300,
                "cull_frequency": 3,
            },
        )

    def process_bird_components(self, contents: str) -> str:
        if not BIRD_PATTERN.search(contents):
            return contents

        while BIRD_PATTERN.search(contents):
            contents = BIRD_PATTERN.sub(self.replace_bird, contents)

        return contents

    def replace_bird(self, match: re.Match | None) -> str:
        if match is None:
            msg = "Invalid bird component: no match found"
            raise ValueError(msg)

        content = match.group(0)
        cache_key = f"bird_template_{hashlib.sha256(content.encode()).hexdigest()}"

        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        component = match.group(1)
        attributes = match.group(2).strip()
        inner_content = match.group(3) if match.group(3) is not None else ""

        start_tag_parts = [
            "{%",
            "bird_component",
            f"'{component}'",
        ]
        if attributes:
            start_tag_parts.append(attributes)
        start_tag_parts.append("%}")

        bird_component = [
            " ".join(start_tag_parts),
            inner_content,
            "{% endbird_component %}",
        ]

        result = mark_safe("".join(bird_component))
        self.cache.set(cache_key, result, timeout=None)

        return result
