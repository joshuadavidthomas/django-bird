from __future__ import annotations

from dataclasses import dataclass

from django import template
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from django_bird._typing import TagBits


@dataclass
class Param:
    name: str
    value: str | bool | None

    def render(self, context: Context) -> str:
        if self.value is None:
            return ""
        if isinstance(self.value, bool) and self.value:
            return self.name
        try:
            value = template.Variable(str(self.value)).resolve(context)
        except template.VariableDoesNotExist:
            value = self.value
        return f'{self.name}="{value}"'

    @classmethod
    def from_bit(cls, bit: str):
        if "=" in bit:
            name, value = bit.split("=", 1)
            value = value.strip("'\"")
        else:
            name, value = bit, True
        return cls(name, value)


@dataclass
class Params:
    attrs: list[Param]

    def render_attrs(self, context: Context) -> SafeString:
        rendered = " ".join(attr.render(context) for attr in self.attrs)
        return mark_safe(rendered)

    @classmethod
    def from_bits(cls, bits: TagBits):
        params: list[Param] = []
        for bit in bits:
            param = Param.from_bit(bit)
            params.append(param)
        return cls(attrs=params)
