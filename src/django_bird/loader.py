from __future__ import annotations

import hashlib
import re

from django.core.cache import cache
from django.template.base import Node
from django.template.base import Origin
from django.template.base import Template
from django.template.context import Context
from django.template.engine import Engine
from django.template.loader_tags import ExtendsNode
from django.template.loader_tags import IncludeNode
from django.template.loaders.filesystem import Loader as FileSystemLoader

from ._typing import override
from .compiler import Compiler
from .components import components
from .staticfiles import ComponentAssetRegistry
from .templatetags.tags.bird import TAG
from .templatetags.tags.bird import BirdNode

BIRD_TAG_PATTERN = re.compile(rf"{{%\s*{TAG}\s+([^\s%}}]+)")


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.compiler = Compiler()
        self.asset_registry = ComponentAssetRegistry()

    @override
    def get_contents(self, origin: Origin) -> str:
        contents = super().get_contents(origin)

        if not BIRD_TAG_PATTERN.search(contents):
            return contents

        template = Template(contents, origin=origin, engine=self.engine)
        context = Context()
        with context.bind_template(template):
            self._scan_for_components(template, context)

        cache_key = f"bird_component_{hashlib.md5(contents.encode()).hexdigest()}"
        compiled = cache.get(cache_key)
        if compiled is None:
            compiled = self.compiler.compile(contents)
            cache.set(cache_key, compiled, timeout=None)
        return compiled

    def _scan_for_components(self, template: Template | Node, context: Context) -> None:
        if not hasattr(template, "nodelist"):
            return

        for node in template.nodelist:
            if isinstance(node, BirdNode):
                component = components.get_component(node.name)
                self.asset_registry.register(component)

            if isinstance(node, ExtendsNode):
                parent_template = node.get_parent(context)
                self._scan_for_components(parent_template, context)

            if isinstance(node, IncludeNode):
                template_name = node.template.token.strip("'\"")
                included_template = self.engine.get_template(template_name)
                self._scan_for_components(included_template, context)

            if hasattr(node, "nodelist"):
                self._scan_for_components(node, context)
