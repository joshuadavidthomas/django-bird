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

from ._typing import _has_nodelist
from ._typing import override
from .compiler import Compiler
from .components import components
from .templatetags.tags.bird import TAG
from .templatetags.tags.bird import BirdNode

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

        template = Template(contents, origin=origin, engine=self.engine)
        context = Context()
        with context.bind_template(template):
            self._ensure_components_loaded(template, context)

        cache_key = f"bird_component_{hashlib.md5(contents.encode()).hexdigest()}"
        compiled = cache.get(cache_key)
        if compiled is None:
            compiled = self.compiler.compile(contents)
            cache.set(cache_key, compiled, timeout=None)
        return compiled

    def _ensure_components_loaded(
        self, node: Template | Node, context: Context
    ) -> None:
        """Ensure all components used in the template are loaded."""
        if isinstance(node, BirdNode):
            components.get_component(node.name)

        if not _has_nodelist(node) or node.nodelist is None:
            return

        for child in node.nodelist:
            if isinstance(child, BirdNode):
                components.get_component(child.name)

            if isinstance(child, ExtendsNode):
                parent_template = child.get_parent(context)
                self._ensure_components_loaded(parent_template, context)

            if isinstance(child, IncludeNode):
                template_name = child.template.token.strip("'\"")
                included_template = self.engine.get_template(template_name)
                self._ensure_components_loaded(included_template, context)

            if hasattr(child, "nodelist"):
                self._ensure_components_loaded(child, context)
