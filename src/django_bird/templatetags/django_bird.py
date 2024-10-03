# pyright: reportAny=false
from __future__ import annotations

from typing import cast

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from django_bird._typing import override

register = template.Library()


@register.tag(name="bird")
def do_bird(parser: Parser, token: Token) -> BirdNode:
    bits = token.split_contents()

    if len(bits) < 2:
        msg = f"{token.contents.split()[0]} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    # {% bird name %}
    # {% bird 'name' %}
    # {% bird "name" %}
    name = bits[1].strip("'\"")
    attrs = bits[2:]

    nodelist = parser.parse(("endbird",))
    parser.delete_first_token()

    return BirdNode(name, attrs, nodelist)


class BirdNode(template.Node):
    def __init__(self, name: str, attrs: list[str], nodelist: NodeList) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist
        self.default_slot = "default"

    @override
    def render(self, context: Context) -> SafeString:
        rendered_slots = self.render_slots(context)

        context = {
            "attrs": self.flat_attrs(context),
            "slot": mark_safe(
                rendered_slots.get(self.default_slot) or context.get("slot")
            ),
            "slots": {
                name: mark_safe(content) for name, content in rendered_slots.items()
            },
        }

        return render_to_string(f"bird/{self.name}.html", context)

    def render_slots(self, context: Context) -> dict[str, str]:
        contents: dict[str, list[str]] = {self.default_slot: []}
        active_slot = self.default_slot

        for node in self.nodelist:
            if isinstance(node, SlotNode):
                active_slot = node.name
                contents.setdefault(active_slot, [])

            rendered_content = node.render(context)
            contents[active_slot].append(rendered_content)

        if (
            all(not content for content in contents[self.default_slot])
            and "slot" in context
        ):
            contents[self.default_slot] = [context["slot"]]

        return {
            slot: template.Template("".join(content)).render(context)
            for slot, content in contents.items()
        }

    def flat_attrs(self, context: Context) -> str:
        attrs: dict[str, str | None | bool] = {}

        for attr in self.attrs:
            if "=" in attr:
                key, value = attr.split("=", 1)
                attrs[key] = template.Variable(value).resolve(context)
            else:
                attrs[attr] = True

        return mark_safe(
            " ".join(
                f'{key}="{value}"' if value else key
                for key, value in attrs.items()
                if not value
            )
        )


@register.tag
def slot(parser: Parser, token: Token) -> SlotNode:
    bits = token.split_contents()

    name = parse_slot_name(bits)

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()

    return SlotNode(name, nodelist)


def parse_slot_name(tag_args: list[str]) -> str:
    if len(tag_args) == 1:
        return "default"
    elif len(tag_args) == 2:
        name = tag_args[1]
        if name.startswith("name="):
            name = name.split("=")[1]
        else:
            name = name
        return name.strip("'\"")
    else:
        raise template.TemplateSyntaxError(
            "slot tag requires either no arguments, one argument, or 'name=\"slot_name\"'"
        )


class SlotNode(template.Node):
    def __init__(self, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    @override
    def render(self, context: Context) -> SafeString:
        default_content: str = self.nodelist.render(context)
        slots = context.get("slots")

        if not slots or not isinstance(slots, dict):
            slot_content = default_content
        else:
            slots_dict = cast(dict[str, str], slots)
            slot_content = slots_dict.get(self.name, default_content)

        # Recursively process the slot content
        t = template.Template(slot_content)
        content = t.render(context)

        return mark_safe(content)
