from __future__ import annotations

import hashlib
import re

from django.core.cache import cache
from django.template.base import Origin
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist
from django.template.loaders.filesystem import Loader as FileSystemLoader

from ._typing import override
from .compiler import BIRD_PATTERN
from .compiler import Compiler
from .components import components
from .staticfiles import ComponentAssetRegistry


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.compiler = Compiler()
        self.asset_registry = ComponentAssetRegistry()

    @override
    def get_contents(self, origin: Origin) -> str:
        contents = super().get_contents(origin)

        self._scan_for_components(contents)

        extends_match = re.search(r'{%\s*extends\s+[\'"]([^\'"]+)[\'"]', contents)
        if extends_match:
            parent_template = extends_match.group(1)
            try:
                parent_contents = self.get_template(parent_template).source
                self._scan_for_components(parent_contents)
            except TemplateDoesNotExist:
                pass

        if not BIRD_PATTERN.search(contents):
            return contents

        cache_key = f"bird_component_{hashlib.md5(contents.encode()).hexdigest()}"
        compiled = cache.get(cache_key)
        if compiled is None:
            compiled = self.compiler.compile(contents)
            cache.set(cache_key, compiled, timeout=None)
        return compiled

    def _scan_for_components(self, contents: str) -> None:
        for match in re.finditer(r"{%\s*bird\s+([^\s%}]+)", contents):
            component_name = match.group(1).strip("'\"")
            component = components.get_component(component_name)
            self.asset_registry.register(component)
