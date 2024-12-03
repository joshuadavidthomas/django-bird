# pyright: reportAny=false
from __future__ import annotations

from django import template
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import TagBits
from django_bird._typing import override

TAG = "bird:prop"


def do_prop(parser: Parser, token: Token) -> PropNode:
    bits = token.split_contents()
    name, default = parse_prop_name(bits)
    attrs = parse_attrs(bits)
    return PropNode(name, default, attrs)


def parse_prop_name(bits: TagBits) -> tuple[str, str | None]:
    if len(bits) <= 1:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    try:
        name, default = bits[1].split("=")
        return name, default.strip("'\"")
    except ValueError:
        return bits[1], None


def parse_attrs(bits: TagBits) -> TagBits:
    return bits[2:]


class PropNode(template.Node):
    def __init__(self, name: str, default: str | None, attrs: TagBits):
        self.name = name
        self.default = default
        self.attrs = attrs

    @override
    def render(self, context: Context) -> str:
        return ""
