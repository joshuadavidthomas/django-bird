from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.template.base import NodeList
from django.template.context import Context

from django_bird.components.attrs import Attrs


@dataclass
class Prop:
    name: str
    value: str | bool | None = None

    def __str__(self) -> str:
        return self.value or ""


@dataclass
class Props:
    props: list[Prop]

    def __getattr__(self, name: str):
        return self.get(name)

    def __getitem__(self, key: int | str):
        if isinstance(key, int):
            return self.props[key]
        else:
            return self.get(key)

    def get(self, name: str, fallback: Any | None = None):
        for prop in self.props:
            if prop.name == name:
                return prop
        return fallback

    @classmethod
    def collect(cls, nodelist: NodeList | None, context: Context, attrs: Attrs):
        from django_bird.templatetags.tags.prop import PropNode

        if nodelist is None:
            return cls([])

        props = []

        for node in nodelist:
            if not isinstance(node, PropNode):
                continue

            attr = attrs.get(node.name)
            if attr:
                value = attr.value
            else:
                value = node.default

            props.append(Prop(name=node.name, value=value))

        return cls(props)
