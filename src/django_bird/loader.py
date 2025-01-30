from __future__ import annotations

import hashlib
import re

from django.core.cache import cache
from django.template.base import Origin
from django.template.engine import Engine
from django.template.loaders.filesystem import Loader as FileSystemLoader

from ._typing import override
from .compiler import Compiler
from .templatetags.tags.bird import TAG

BIRD_TAG_PATTERN = re.compile(rf"{{%\s*{TAG}\s+([^\s%}}]+)")


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.compiler = Compiler()

    @override
    def get_contents(self, origin: Origin) -> str:
        contents = super().get_contents(origin)

        if not BIRD_TAG_PATTERN.search(contents):
            return contents

        cache_key = f"bird_component_{hashlib.md5(contents.encode()).hexdigest()}"
        compiled = cache.get(cache_key)
        if compiled is None:
            compiled = self.compiler.compile(contents)
            cache.set(cache_key, compiled, timeout=None)
        return compiled
