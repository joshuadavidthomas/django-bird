# pyright: reportAny=false
from __future__ import annotations

from typing import final

from django import template
from django.template.base import FilterExpression
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import RawTagBits
from django_bird._typing import override

TAG = "bird:prop"


def do_prop(parser: Parser, token: Token) -> PropNode:
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    prop = bits.pop(0)

    try:
        name, default = prop.split("=", 1)
    except ValueError:
        name = prop
        default = "None"

    return PropNode(name, parser.compile_filter(default), bits)


@final
class PropNode(template.Node):
    def __init__(self, name: str, default: FilterExpression, attrs: RawTagBits):
        self.name = name
        self.default = default
        self.attrs = attrs

    @override
    def render(self, context: Context) -> str:
        return ""
