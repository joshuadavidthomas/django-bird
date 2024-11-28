from __future__ import annotations

from dataclasses import dataclass

from django import template
from django.template.base import NodeList
from django.template.context import Context
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

DEFAULT_SLOT = "default"


@dataclass
class Slot:
    content: str

    @classmethod
    def from_nodelist(cls, nodelist: NodeList, context: Context) -> Slot:
        rendered = nodelist.render(context)
        return cls(content=rendered)

    def render(self, context: Context) -> SafeString:
        return mark_safe(template.Template(self.content).render(context))


@dataclass
class Slots:
    slots: dict[str, Slot]
    context: Context  # Need to keep context reference

    @classmethod
    def create(cls, nodelist: NodeList | None, context: Context) -> Slots:
        from django_bird.templatetags.tags.slot import SlotNode

        slots: dict[str, Slot] = {DEFAULT_SLOT: Slot("")}

        if not nodelist:
            if "slot" in context:
                slots[DEFAULT_SLOT] = Slot(context["slot"])
            return cls(slots, context)

        current_slot = DEFAULT_SLOT
        slot_contents: dict[str, list[str]] = {DEFAULT_SLOT: []}

        # Collect all content first
        for node in nodelist:
            if isinstance(node, SlotNode):
                current_slot = node.name
                slot_contents.setdefault(current_slot, [])
            else:
                content = node.render(context)
                slot_contents[current_slot].append(content)

        # Handle empty default slot with parent slot content
        if (
            all(not content for content in slot_contents[DEFAULT_SLOT])
            and "slot" in context
        ):
            slot_contents[DEFAULT_SLOT] = [context["slot"]]

        # Create slots from collected content
        slots = {
            name: Slot("".join(contents)) for name, contents in slot_contents.items()
        }

        return cls(slots, context)

    def get_slot(self, name: str, default: str | None = None) -> Slot | None:
        slot = self.slots.get(name)
        if not slot and default is not None:
            return Slot(default)
        return slot

    def render(self) -> dict[str, SafeString]:
        return {name: slot.render(self.context) for name, slot in self.slots.items()}

    @property
    def default(self) -> SafeString | None:
        if slot := self.get_slot(DEFAULT_SLOT):
            return slot.render(self.context)
        return None
