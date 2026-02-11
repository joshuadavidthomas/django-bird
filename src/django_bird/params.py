from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from django import template
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
                if node.name != attr.name:
                    continue

                resolved = (
                    attr.value.resolve(context)
                    if isinstance(attr.value, Value)
                    else attr.value
                )
                if resolved is not None:
                    value = (
                        attr.value
                        if isinstance(attr.value, Value)
                        else Value(attr.value)
                    )
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
    raw: FilterExpression | str | bool | None

    def resolve(self, context: Context | dict[str, Any], is_attr: bool = False) -> Any:
        match self.raw:
            case None:
                return None
            case bool(b):
                return b if b else None
            case str(raw_str):
                return self._resolve_raw_string(raw_str, context)
            case FilterExpression() as expression:
                expression_context = (
                    context if isinstance(context, Context) else Context(context)
                )
                return self._resolve_expression(
                    expression,
                    expression_context,
                    is_attr,
                )
            case _:
                msg = f"Unsupported value type: {type(self.raw)!r}"
                raise TypeError(msg)

    def _resolve_expression(
        self,
        expression: FilterExpression,
        context: Context,
        is_attr: bool,
    ) -> Any:
        if expression.token == "False":
            return None

        var_resolve = getattr(expression.var, "resolve", None)
        if not expression.filters and callable(var_resolve):
            try:
                var_resolve(context)
            except VariableDoesNotExist:
                return expression.token

        value = expression.resolve(context)
        if is_attr and value is False:
            return None
        return value

    def _resolve_raw_string(self, raw: str, context: Context | dict[str, Any]) -> Any:
        if raw == "False":
            return None
        if raw == "True":
            return True
        if self._is_quoted(raw):
            return raw[1:-1]

        try:
            return template.Variable(raw).resolve(context)
        except template.VariableDoesNotExist:
            return raw

    @staticmethod
    def _is_quoted(raw: str) -> bool:
        return raw.startswith(("'", '"')) and raw.endswith(raw[0])
