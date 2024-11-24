# pyright: reportAny=false
from __future__ import annotations

from typing import Any
from typing import cast

from django import template
from django.template.base import NodeList
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.template.loader import select_template
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from django_bird._typing import override
from django_bird.conf import app_settings

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

    # self-closing tag
    # {% bird name / %}
    if len(attrs) > 0 and attrs[-1] == "/":
        nodelist = None
    else:
        nodelist = parser.parse(("endbird",))
        parser.delete_first_token()

    return BirdNode(name, attrs, nodelist)


class BirdNode(template.Node):
    def __init__(self, name: str, attrs: list[str], nodelist: NodeList | None) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist
        self.default_slot = "default"

    @override
    def render(self, context: Context) -> SafeString:
        component_name = self.get_component_name(context)
        component_context = self.get_component_context_data(context)
        template_names = self.get_template_names(component_name)
        template = select_template(template_names)
        return template.render(component_context)

    def get_component_name(self, context: Context) -> str:
        try:
            name = template.Variable(self.name).resolve(context)
        except template.VariableDoesNotExist:
            name = self.name
        return name

    def get_component_context_data(self, context: Context) -> dict[str, Any]:
        rendered_slots = self.render_slots(context)
        flat_attrs = self.flatten_attrs(context)
        default_slot = rendered_slots.get(self.default_slot) or context.get("slot")
        return {
            "attrs": mark_safe(flat_attrs),
            "slot": mark_safe(default_slot),
            "slots": {
                name: mark_safe(content) for name, content in rendered_slots.items()
            },
        }

    def render_slots(self, context: Context) -> dict[str, str]:
        if self.nodelist is None:
            return {}

        contents: dict[str, list[str]] = {self.default_slot: []}
        active_slot = self.default_slot

        for node in self.nodelist:
            if isinstance(node, SlotNode):
                active_slot = node.name
                contents.setdefault(active_slot, [])
            else:
                active_slot = self.default_slot

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

    def flatten_attrs(self, context: Context) -> str:
        attrs: dict[str, str | None | bool] = {}

        for attr in self.attrs:
            if "=" in attr:
                key, value = attr.split("=", 1)
                attrs[key] = template.Variable(value).resolve(context)
            else:
                attrs[attr] = True

        return " ".join(
            key if isinstance(value, bool) and value else f'{key}="{value}"'
            for key, value in attrs.items()
        )

    def get_template_names(self, name: str) -> list[str]:
        """
        Generate a list of potential template names for a component.

        The function searches for templates in the following order (from most specific to most general):

        1. In a subdirectory named after the component, using the component name
        2. In the same subdirectory, using a fallback 'index.html'
        3. In parent directory for nested components
        4. In the base component directory, using the full component name

        The order of names is important as it determines the template resolution priority.
        This order allows for both direct matches and hierarchical component structures,
        with more specific paths taking precedence over more general ones.

        This order allows for:
        - Single file components
        - Multi-part components
        - Specific named files within component directories
        - Fallback default files for components

        For example:
        - For an "input" component, the ordering would be:
            1. `{component_dir}/input/input.html`
            2. `{component_dir}/input/index.html`
            3. `{component_dir}/input.html`
        - For an "input.label" component:
            1. `{component_dir}/input/label/label.html`
            2. `{component_dir}/input/label/index.html`
            3. `{component_dir}/input/label.html`
            4. `{component_dir}/input.label.html`

        Returns:
            list[str]: A list of potential template names in resolution order.
        """
        template_names = []
        component_dirs = list(dict.fromkeys([*app_settings.COMPONENT_DIRS, "bird"]))

        name_parts = name.split(".")
        path_name = "/".join(name_parts)

        for component_dir in component_dirs:
            potential_names = [
                f"{component_dir}/{path_name}/{name_parts[-1]}.html",
                f"{component_dir}/{path_name}/index.html",
                f"{component_dir}/{path_name}.html",
                f"{component_dir}/{self.name}.html",
            ]
            template_names.extend(potential_names)

        return list(dict.fromkeys(template_names))


@register.tag("bird:slot")
def do_slot(parser: Parser, token: Token) -> SlotNode:
    bits = token.split_contents()
    name = parse_slot_name(bits)
    nodelist = parser.parse(("endbird:slot",))
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
