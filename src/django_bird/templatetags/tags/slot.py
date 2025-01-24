# pyright: reportAny=false
from __future__ import annotations

from typing import cast

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from django_bird._typing import TagBits
from django_bird._typing import override

TAG = "bird:slot"
END_TAG = "endbird:slot"

DEFAULT_SLOT = "default"


def do_slot(parser: Parser, token: Token) -> SlotNode:
    bits = token.split_contents()
    name = parse_slot_name(bits)
    nodelist = parse_nodelist(parser)
    return SlotNode(name, nodelist)


def parse_slot_name(bits: TagBits) -> str:
    if len(bits) == 1:
        return DEFAULT_SLOT
    elif len(bits) == 2:
        name = bits[1]
        if name.startswith("name="):
            name = name.split("=")[1]
        else:
            name = name
        return name.strip("'\"")
    else:
        msg = f"{TAG} tag requires either no arguments, one argument, or 'name=\"slot_name\"'"
        raise template.TemplateSyntaxError(msg)


def parse_nodelist(parser: Parser) -> NodeList:
    nodelist = parser.parse((END_TAG,))
    parser.delete_first_token()
    return nodelist


class SlotNode(template.Node):
    def __init__(self, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    @override
    def render(self, context: Context) -> SafeString:
        default_content: str = self.nodelist.render(context)
        slots = context.get("slots")

        if not slots or not isinstance(slots, dict):
            return mark_safe(default_content)

        slots_dict = cast(dict[str, str], slots)
        slot_content = slots_dict.get(self.name)

        if slot_content is None or slot_content == "":
            return mark_safe(default_content)

        t = template.Template(slot_content)
        content = t.render(context)
        return mark_safe(content)
