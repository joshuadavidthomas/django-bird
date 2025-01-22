# pyright: reportAny=false
from __future__ import annotations

from typing import Any

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import TagBits
from django_bird._typing import override
from django_bird.components import Component
from django_bird.components import components
from django_bird.conf import app_settings
from django_bird.params import Param
from django_bird.params import Params
from django_bird.params import Value
from django_bird.slots import DEFAULT_SLOT
from django_bird.slots import Slots

TAG = "bird"
END_TAG = "endbird"


def do_bird(parser: Parser, token: Token) -> BirdNode:
    bits = token.split_contents()
    if len(bits) == 1:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    name = bits[1]
    attrs = []
    isolated_context = False

    for bit in bits[2:]:
        match bit:
            case "only":
                isolated_context = True
            case "/":
                continue
            case _:
                param = Param.from_bit(bit)
                attrs.append(param)

    nodelist = parse_nodelist(bits, parser)
    return BirdNode(name, attrs, nodelist, isolated_context)


def parse_nodelist(bits: TagBits, parser: Parser) -> NodeList | None:
    # self-closing tag
    # {% bird name / %}
    if len(bits) > 0 and bits[-1] == "/":
        nodelist = None
    else:
        nodelist = parser.parse((END_TAG,))
        parser.delete_first_token()
    return nodelist


class BirdNode(template.Node):
    def __init__(
        self,
        name: str,
        attrs: list[Param],
        nodelist: NodeList | None,
        isolated_context: bool = False,
    ) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist
        self.isolated_context = isolated_context

    @override
    def render(self, context: Context) -> str:
        component_name = self.get_component_name(context)
        component = components.get_component(component_name)
        component_context = self.get_component_context_data(component, context)

        if self.isolated_context:
            return component.render(context.new(component_context))
        with context.push(**component_context):
            return component.render(context)

    def get_component_name(self, context: Context) -> str:
        try:
            name = template.Variable(self.name).resolve(context)
        except template.VariableDoesNotExist:
            name = self.name
        return name

    def get_component_context_data(
        self, component: Component, context: Context
    ) -> dict[str, Any]:
        if app_settings.ENABLE_BIRD_ID_ATTR:
            self.attrs.append(Param("data_bird_id", Value(component.id, True)))

        params = Params.with_attrs(self.attrs)
        props = params.render_props(component.nodelist, context)
        attrs = params.render_attrs(context)
        slots = Slots.collect(self.nodelist, context).render()
        default_slot = slots.get(DEFAULT_SLOT) or context.get("slot")

        return {
            "attrs": attrs,
            "props": props,
            "slot": default_slot,
            "slots": slots,
        }
