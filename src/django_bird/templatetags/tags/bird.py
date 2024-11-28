# pyright: reportAny=false
from __future__ import annotations

from typing import Any

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.template.loader import select_template
from django.utils.safestring import SafeString

from django_bird._typing import TagBits
from django_bird._typing import override
from django_bird.components.attrs import Attrs
from django_bird.components.slots import DEFAULT_SLOT
from django_bird.components.slots import Slots
from django_bird.components.templates import get_template_names

TAG = "bird"
END_TAG = "endbird"


def do_bird(parser: Parser, token: Token) -> BirdNode:
    bits = token.split_contents()
    name = parse_bird_name(bits)
    attrs = parse_attrs(bits)
    nodelist = parse_nodelist(attrs, parser)
    return BirdNode(name, attrs, nodelist)


def parse_bird_name(bits: TagBits) -> str:
    if len(bits) == 1:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    # {% bird name %}
    # {% bird 'name' %}
    # {% bird "name" %}
    return bits[1].strip("'\"")


def parse_attrs(bits: TagBits) -> TagBits:
    return bits[2:]


def parse_nodelist(attrs: TagBits, parser: Parser) -> NodeList | None:
    # self-closing tag
    # {% bird name / %}
    if len(attrs) > 0 and attrs[-1] == "/":
        nodelist = None
    else:
        nodelist = parser.parse((END_TAG,))
        parser.delete_first_token()
    return nodelist


class BirdNode(template.Node):
    def __init__(self, name: str, attrs: list[str], nodelist: NodeList | None) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist

    @override
    def render(self, context: Context) -> SafeString:
        component_name = self.get_component_name(context)
        component_context = self.get_component_context_data(context)
        template_names = get_template_names(component_name)
        template = select_template(template_names)
        return template.render(component_context)

    def get_component_name(self, context: Context) -> str:
        try:
            name = template.Variable(self.name).resolve(context)
        except template.VariableDoesNotExist:
            name = self.name
        return name

    def get_component_context_data(self, context: Context) -> dict[str, Any]:
        attrs = Attrs.parse(self.attrs, context)
        slots = Slots.collect(self.nodelist, context).render()
        default_slot = slots.get(DEFAULT_SLOT) or context.get("slot")
        return {
            "attrs": attrs.flatten(),
            "slot": default_slot,
            "slots": slots,
        }
