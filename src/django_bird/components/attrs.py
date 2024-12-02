from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django import template
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from django_bird._typing import TagBits


@dataclass
class Attr:
    name: str
    value: str | bool

    def render(self, context: Context) -> str:
        if isinstance(self.value, bool) and self.value:
            return self.name
        try:
            value = template.Variable(self.value).resolve(context)
        except template.VariableDoesNotExist:
            value = self.value
        return f'{self.name}="{value}"'


@dataclass
class Attrs:
    attrs: list[Attr]

    def __getitem__(self, key: int):
        return self.attrs[key]

    def __iter__(self):
        yield from self.attrs

    def __len__(self):
        return len(self.attrs)

    def get(self, name: str, fallback: Any | None = None):
        for attr in self.attrs:
            if attr.name == name:
                return attr
        return fallback

    @classmethod
    def from_tag_bits(cls, raw_attrs: TagBits) -> Attrs:
        parsed = []
        for attr in raw_attrs:
            if "=" in attr:
                name, value = attr.split("=", 1)
                parsed.append(Attr(name=name, value=value.strip("'\"")))
            else:
                parsed.append(Attr(name=attr, value=True))
        return cls(parsed)

    def flatten(self, context: Context) -> SafeString:
        rendered = " ".join(attr.render(context) for attr in self.attrs)
        return mark_safe(rendered)
