from __future__ import annotations

from dataclasses import dataclass

from django import template
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe


@dataclass
class Attr:
    name: str
    value: str | bool

    def render(self) -> str:
        if isinstance(self.value, bool) and self.value:
            return self.name
        return f'{self.name}="{self.value}"'


@dataclass
class Attrs:
    attrs: list[Attr]

    @classmethod
    def parse(cls, raw_attrs: list[str], context: Context) -> Attrs:
        parsed = []
        for attr in raw_attrs:
            if "=" in attr:
                name, value = attr.split("=", 1)
                resolved_value = template.Variable(value).resolve(context)
                parsed.append(Attr(name=name, value=resolved_value))
            else:
                parsed.append(Attr(name=attr, value=True))
        return cls(parsed)

    def flatten(self) -> SafeString:
        rendered = " ".join(attr.render() for attr in self.attrs)
        return mark_safe(rendered)
