from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.template.base import FilterExpression
from django.template.base import Node
from django.template.base import NodeList
from django.template.base import TextNode
from django.template.base import Variable
from django.template.base import VariableNode
from django.template.context import Context

from django_bird.templatetags.tags.slot import DEFAULT_SLOT
from django_bird.templatetags.tags.slot import SlotNode

if TYPE_CHECKING:
    from django_bird.components import BoundComponent


@dataclass
class Slots:
    slots: dict[str, Slot]

    def __len__(self):
        return len(self.slots)

    def render(self, bound_component: BoundComponent, context: Context):
        if bound_component.nodelist is None:
            return {}

        slot_nodes = {
            node.name: node.nodelist
            for node in bound_component.nodelist
            if isinstance(node, SlotNode)
        }
        default_nodes = NodeList(
            [
                node
                for node in bound_component.nodelist
                if not isinstance(node, SlotNode)
            ]
        )

        slots = {DEFAULT_SLOT: default_nodes, **slot_nodes}

        if context.get("slots"):
            for name, content in context["slots"].items():
                if name not in slots or not slots.get(name):
                    slots[name] = NodeList([TextNode(str(content))])

        if not slots[DEFAULT_SLOT] and "slot" in context:
            slots[DEFAULT_SLOT] = NodeList([TextNode(context["slot"])])

        return {
            name: nodelist.render(context)
            for name, nodelist in slots.items()
            if nodelist
        }

    @classmethod
    def collect(cls, nodelist: NodeList):
        slots: dict[str, Slot] = {}

        for node in nodelist:
            slot = Slot.from_node(node)
            if slot is None:
                continue
            slots[slot.name] = slot

            if hasattr(node, "nodelist"):
                nested = cls.collect(node.nodelist)
                slots.update(nested.slots)

        return cls(slots)


@dataclass
class Slot:
    name: str
    node: SlotNode | VariableNode

    @classmethod
    def from_node(cls, node: Node):
        match node:
            case VariableNode(
                filter_expression=FilterExpression(
                    var=Variable(var=name),
                )
            ) if name == "slot":
                slot_name = DEFAULT_SLOT
            case SlotNode(name=name) if name == DEFAULT_SLOT:
                slot_name = DEFAULT_SLOT
            case VariableNode(
                filter_expression=FilterExpression(
                    var=Variable(var=name),
                )
            ) if name.startswith("slots."):
                slot_name = name.replace("slots.", "")
            case SlotNode(name=name):
                slot_name = name
            case _:
                return

        return cls(name=slot_name, node=node)
