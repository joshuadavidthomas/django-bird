from __future__ import annotations

import hashlib

from django.core.cache import cache
from django.template.base import Origin
from django.template.engine import Engine
from django.template.loaders.filesystem import Loader as FileSystemLoader

from ._typing import override
from .compiler import BIRD_PATTERN
from .compiler import Compiler


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.compiler = Compiler()

    @override
    def get_contents(self, origin: Origin) -> str:
        contents = super().get_contents(origin)
        if not BIRD_PATTERN.search(contents):
            return contents
        cache_key = f"bird_component_{hashlib.md5(contents.encode()).hexdigest()}"
        compiled = cache.get(cache_key)  # pyright: ignore[reportAny]
        if compiled is None:
            compiled = self.compiler.compile(contents)
            cache.set(cache_key, compiled, timeout=None)
        return compiled
