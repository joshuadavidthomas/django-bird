# pyright: reportAny=false
from __future__ import annotations

from typing import final

from django import template
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import RawTagBits
from django_bird._typing import override

TAG = "bird:load"


def do_load(_parser: Parser, token: Token) -> LoadNode:
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{TAG} tag requires at least one component name"
        raise template.TemplateSyntaxError(msg)

    component_names = [bit.strip("\"'") for bit in bits]
    return LoadNode(component_names=component_names)


@final
class LoadNode(template.Node):
    def __init__(self, component_names: RawTagBits):
        self.component_names = component_names

    @override
    def render(self, context: Context) -> str:
        return ""
