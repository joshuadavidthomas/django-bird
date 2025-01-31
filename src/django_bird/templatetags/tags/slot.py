# pyright: reportAny=false
from __future__ import annotations

from typing import cast
from typing import final

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.utils.safestring import SafeString

from django_bird._typing import override

TAG = "bird:slot"
END_TAG = "endbird:slot"

DEFAULT_SLOT = "default"


def do_slot(parser: Parser, token: Token) -> SlotNode:
    _tag, *bits = token.split_contents()
    if len(bits) > 1:
        msg = f"{TAG} tag requires either one or no arguments"
        raise template.TemplateSyntaxError(msg)

    if len(bits) == 0:
        name = DEFAULT_SLOT
    else:
        name = bits[0]
        if name.startswith("name="):
            _, name = name.split("=")
        name = name.strip("'\"")

    nodelist = parser.parse((END_TAG,))
    parser.delete_first_token()

    return SlotNode(name, nodelist)


@final
class SlotNode(template.Node):
    def __init__(self, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    @override
    def render(self, context: Context) -> SafeString:
        slots = context.get("slots")

        if not slots or not isinstance(slots, dict):
            return self.nodelist.render(context)

        slots_dict = cast(dict[str, str], slots)
        slot_content = slots_dict.get(self.name)

        if slot_content is None or slot_content == "":
            return self.nodelist.render(context)

        return template.Template(slot_content).render(context)
