from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from django import template
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from .templatetags.tags.prop import PropNode

if TYPE_CHECKING:
    from django_bird.components import Component


@dataclass
class Params:
    attrs: list[Param] = field(default_factory=list)
    props: list[Param] = field(default_factory=list)

    @classmethod
    def with_attrs(cls, attrs: list[Param] | None) -> Params:
        """Create a Params instance with a copy of the provided attrs."""
        return cls(attrs=attrs.copy() if attrs is not None else [], props=[])

    def render_props(self, component: Component, context: Context):
        if component.nodelist is None:
            return

        attrs_to_remove = set()

        for node in component.nodelist:
            if not isinstance(node, PropNode):
                continue

            value = Value(node.default, quoted=False)

            for idx, attr in enumerate(self.attrs):
                if node.name == attr.name:
                    resolved = attr.value.resolve(context)
                    if resolved is not None:
                        value = attr.value
                    attrs_to_remove.add(idx)

            self.props.append(Param(name=node.name, value=value))

        for idx in sorted(attrs_to_remove, reverse=True):
            self.attrs.pop(idx)

        return {prop.name: prop.render_prop(context) for prop in self.props}

    def render_attrs(self, context: Context) -> SafeString:
        rendered = " ".join(attr.render_attr(context) for attr in self.attrs)
        return mark_safe(rendered)


@dataclass
class Param:
    name: str
    value: Value

    def render_attr(self, context: Context) -> str:
        value = self.value.resolve(context)
        name = self.name.replace("_", "-")
        if value is None:
            return ""
        if value is True:
            return name
        return f'{name}="{value}"'

    def render_prop(self, context: Context) -> str | bool | None:
        return self.value.resolve(context)

    @classmethod
    def from_bit(cls, bit: str) -> Param:
        if "=" in bit:
            name, raw_value = bit.split("=", 1)
            # Check if the value is quoted
            if raw_value.startswith(("'", '"')) and raw_value.endswith(raw_value[0]):
                value = Value(raw_value[1:-1], quoted=True)
            else:
                value = Value(raw_value.strip(), quoted=False)
        else:
            name, value = bit, Value(True)
        return cls(name, value)


@dataclass
class Value:
    raw: str | bool | None
    quoted: bool = False

    def resolve(self, context: Context | dict[str, Any]) -> Any:
        if self.raw is None or (isinstance(self.raw, str) and self.raw == "False"):
            return None
        if (isinstance(self.raw, bool) and self.raw) or (
            isinstance(self.raw, str) and self.raw == "True"
        ):
            return True
        if isinstance(self.raw, str) and not self.quoted:
            try:
                return template.Variable(str(self.raw)).resolve(context)
            except template.VariableDoesNotExist:
                return self.raw
        return self.raw
