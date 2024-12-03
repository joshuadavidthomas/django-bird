from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.template.backends.django import Template
from django.template.loader import select_template

from .cache import LRUCache
from .templates import get_template_names


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    template: Template

    def render(self, context: dict[str, Any]):
        return self.template.render(context)

    @property
    def nodelist(self):
        return self.template.template.nodelist

    @classmethod
    def from_name(cls, name: str):
        template_names = get_template_names(name)
        template = select_template(template_names)
        return cls(name=name, template=template)


class Registry:
    def __init__(self, maxsize: int = 100):
        self._cache: LRUCache[str, Component] = LRUCache(maxsize=maxsize)

    def get_component(self, name: str) -> Component:
        try:
            return self._cache[name]
        except KeyError:
            component = Component.from_name(name)
            self._cache[name] = component
            return component

    def clear(self) -> None:
        """Clear the component cache. Mainly useful for testing."""
        self._cache.clear()


registry = Registry()
