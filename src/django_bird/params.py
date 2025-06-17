from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from django.template.base import FilterExpression
from django.template.base import VariableDoesNotExist
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from .templatetags.tags.bird import BirdNode
from .templatetags.tags.prop import PropNode

if TYPE_CHECKING:
    from django_bird.components import Component


@dataclass
class Params:
    attrs: list[Param] = field(default_factory=list)
    props: list[Param] = field(default_factory=list)

    def render_props(self, component: Component, context: Context):
        if component.nodelist is None:
            return

        attrs_to_remove = set()

        for node in component.nodelist:
            if not isinstance(node, PropNode):
                continue

            value = Value(node.default)

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

    @classmethod
    def from_node(cls, node: BirdNode) -> Params:
        return cls(
            attrs=[Param(key, Value(value)) for key, value in node.attrs.items()],
            props=[],
        )


@dataclass
class Param:
    name: str
    value: Value | str | bool

    def render_attr(self, context: Context) -> str:
        if isinstance(self.value, Value):
            value = self.value.resolve(context, is_attr=True)
        else:
            value = self.value
        if value is None:
            return ""
        name = self.name.replace("_", "-")
        if value is True:
            return name
        return f'{name}="{value}"'

    def render_prop(self, context: Context) -> str | bool | None:
        return (
            self.value.resolve(context) if isinstance(self.value, Value) else self.value
        )


@dataclass
class Value:
    raw: FilterExpression

    def resolve(self, context: Context | dict[str, Any], is_attr=False) -> Any:
        if is_attr and self.raw.token == "False":
            return None
        if self.raw.is_var:
            try:
                self.raw.var.resolve(context)
            except VariableDoesNotExist:
                return self.raw.token
        return self.raw.resolve(context)
