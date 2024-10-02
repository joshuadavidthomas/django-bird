from __future__ import annotations

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.tag
def bird_component(parser, token):
    bits = token.split_contents()

    if len(bits) < 2:
        msg = f"{token.contents.split()[0]} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    # {% bird_component name %}
    # {% bird_component 'name' %}
    # {% bird_component "name" %}
    component_type = bits[1].strip("'\"")
    attrs = bits[2:]

    nodelist = parser.parse(("endbird_component",))
    parser.delete_first_token()

    return BirdComponentNode(component_type, attrs, nodelist)


class BirdComponentNode(template.Node):
    def __init__(self, component_type, attrs, nodelist):
        self.component_type = component_type
        self.attrs = attrs
        self.nodelist = nodelist

    def render(self, context):
        attrs = {}
        for attr in self.attrs:
            key, value = attr.split("=")
            attrs[key] = template.Variable(value).resolve(context)

        print(f"{self.attrs=}")
        print(f"{attrs=}")
        slots = {"default": ""}
        current_slot = "default"
        for node in self.nodelist:
            if isinstance(node, SlotNode):
                current_slot = node.slot_name
                slots[current_slot] = ""
            else:
                slots[current_slot] += node.render(context)

        new_context = {}
        new_context["attrs"] = " ".join(
            f'{key}="{value}"' for key, value in attrs.items() if value is not None
        )
        new_context["slot"] = mark_safe(slots["default"])
        new_context["slots"] = {
            name: mark_safe(content) for name, content in slots.items()
        }

        print(f"{new_context=}")

        return render_to_string(f"bird/{self.component_type}.html", new_context)


@register.tag("slot")
def do_slot(parser, token):
    bits = token.split_contents()

    if len(bits) == 1:
        # {% slot %}
        slot_name = "default"
    elif len(bits) == 2:
        if bits[1].startswith("name="):
            # {% slot name="default" %}
            # {% slot name='default' %}
            slot_name = bits[1].split("=")[1].strip("'\"")
        else:
            # {% slot default %}
            # {% slot "default" %}
            # {% slot 'default' %}
            slot_name = bits[1].strip("'\"")
    else:
        msg = f"{bits[0]} tag requires either no arguments, one argument, or 'name=\"slot_name\"'"
        raise template.TemplateSyntaxError(msg)

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()

    return SlotNode(slot_name, nodelist)


class SlotNode(template.Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        slots = context.get("slots", {})
        return slots.get(self.slot_name, content)
