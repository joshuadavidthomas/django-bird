from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from django import template
from django.template.base import NodeList
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from .templatetags.tags.prop import PropNode


@dataclass
class Value:
    raw: str | bool | None
    quoted: bool = False

    def resolve(self, context: Context | dict[str, Any]) -> Any:
        match (self.raw, self.quoted):
            # Handle special string values and None
            case (None, _) | ("False", _):
                return None
            case ("True", _):
                return True

            # Handle boolean values
            case (bool(boolean), _):
                return boolean

            # Handle quoted strings as literals
            case (str(quoted_string), True):
                return quoted_string

            # Handle everything else as template variables, falling back to raw
            case _:
                raw_string = str(self.raw)
                try:
                    return template.Variable(raw_string).resolve(context)
                except template.VariableDoesNotExist:
                    return raw_string


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
class Params:
    attrs: list[Param] = field(default_factory=list)
    props: list[Param] = field(default_factory=list)

    @classmethod
    def with_attrs(cls, attrs: list[Param] | None) -> Params:
        """Create a Params instance with a copy of the provided attrs."""
        return cls(attrs=attrs.copy() if attrs is not None else [], props=[])

    def render_props(self, nodelist: NodeList | None, context: Context):
        if nodelist is None:
            return

        attrs_to_remove = set()

        for node in nodelist:
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
