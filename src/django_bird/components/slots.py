from __future__ import annotations

from dataclasses import dataclass

from django.template.base import NodeList
from django.template.base import Template
from django.template.context import Context

DEFAULT_SLOT = "default"


@dataclass
class Slots:
    slots: dict[str, list[str]]
    context: Context

    @classmethod
    def collect(cls, nodelist: NodeList | None, context: Context):
        from django_bird.templatetags.tags.slot import SlotNode

        if nodelist is None:
            return cls({}, context)

        slots: dict[str, list[str]] = {DEFAULT_SLOT: []}
        active_slot = DEFAULT_SLOT

        for node in nodelist:
            if isinstance(node, SlotNode):
                active_slot = node.name
                slots.setdefault(active_slot, [])
            else:
                active_slot = DEFAULT_SLOT

            rendered_content = node.render(context)
            slots[active_slot].append(rendered_content)

        if all(not content for content in slots[DEFAULT_SLOT]) and "slot" in context:
            slots[DEFAULT_SLOT] = [context["slot"]]

        return cls(slots, context)

    def render(self):
        return {
            slot: Template("".join(content)).render(self.context)
            for slot, content in self.slots.items()
        }
