from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from django import template
from django.template.base import NodeList
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
        value: str | bool
        if "=" in bit:
            name, value = bit.split("=", 1)
            value = value.strip("'\"")
        else:
            name, value = bit, True
        return cls(name, value)


@dataclass
class Params:
    attrs: list[Param] = field(default_factory=list)
    props: list[Param] = field(default_factory=list)

    def render_props(self, nodelist: NodeList | None, context: Context):
        from django_bird.templatetags.tags.prop import PropNode

        if nodelist is None:
            return

        indices_to_remove = set()

        for node in nodelist:
            if not isinstance(node, PropNode):
                continue

            value: str | bool | None = node.default

            for idx, attr in enumerate(self.attrs):
                if node.name == attr.name:
                    value = attr.value
                    indices_to_remove.add(idx)

            self.props.append(Param(name=node.name, value=value))

        for idx in sorted(indices_to_remove, reverse=True):
            self.attrs.pop(idx)

        return {prop.name: prop.value for prop in self.props}

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
