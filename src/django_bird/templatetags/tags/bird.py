# pyright: reportAny=false
from __future__ import annotations

from typing import final

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import ParsedTagBits
from django_bird._typing import RawTagBits
from django_bird._typing import override

TAG = "bird"
END_TAG = "endbird"


def do_bird(parser: Parser, token: Token) -> BirdNode:
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    name = bits.pop(0)
    attrs: ParsedTagBits = {}
    isolated_context = False

    for bit in bits:
        match bit:
            case "only":
                isolated_context = True
            case "/":
                continue
            case _:
                if "=" in bit:
                    key, value = bit.split("=", 1)
                else:
                    key = bit
                    value = "True"
                attrs[key] = parser.compile_filter(value)

    nodelist = parse_nodelist(bits, parser)
    return BirdNode(name, attrs, nodelist, isolated_context)


def parse_nodelist(bits: RawTagBits, parser: Parser) -> NodeList | None:
    # self-closing tag
    # {% bird name / %}
    if len(bits) > 0 and bits[-1] == "/":
        nodelist = None
    else:
        nodelist = parser.parse((END_TAG,))
        parser.delete_first_token()
    return nodelist


@final
class BirdNode(template.Node):
    def __init__(
        self,
        name: str,
        attrs: ParsedTagBits,
        nodelist: NodeList | None,
        isolated_context: bool = False,
    ) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist
        self.isolated_context = isolated_context

    @override
    def render(self, context: Context) -> str:
        from django_bird.components import components

        component_name = self.get_component_name(context)
        component = components.get_component(component_name)
        bound_component = component.get_bound_component(node=self)

        if self.isolated_context:
            isolated_context = context.new()
            return bound_component.render(
                context=isolated_context,
                resolution_context=context,
            )
        return bound_component.render(context)

    def get_component_name(self, context: Context) -> str:
        try:
            name = template.Variable(self.name).resolve(context)
        except template.VariableDoesNotExist:
            name = self.name
        return name
