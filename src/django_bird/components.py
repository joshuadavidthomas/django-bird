from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Generator
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from hashlib import md5
from pathlib import Path
from threading import Lock
from typing import Any

from django.conf import settings
from django.template.backends.django import Template as DjangoTemplate
from django.template.base import Node
from django.template.base import NodeList
from django.template.base import TextNode
from django.template.context import Context
from django.template.loader import select_template

from .conf import app_settings
from .params import Param
from .params import Params
from .params import Value
from .plugins import pm
from .staticfiles import Asset
from .staticfiles import AssetType
from .templates import find_components_in_template
from .templates import get_component_directories
from .templates import get_template_names
from .templatetags.tags.bird import BirdNode
from .templatetags.tags.slot import DEFAULT_SLOT
from .templatetags.tags.slot import SlotNode


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    template: DjangoTemplate
    assets: frozenset[Asset] = field(default_factory=frozenset)

    def get_asset(self, asset_filename: str) -> Asset | None:
        for asset in self.assets:
            if asset.path.name == asset_filename:
                return asset
        return None

    def get_bound_component(self, node: BirdNode):
        params = Params.from_node(node)
        return BoundComponent(component=self, params=params, nodelist=node.nodelist)

    @property
    def data_attribute_name(self):
        return self.name.replace(".", "-")

    @property
    def id(self):
        normalized_source = "".join(self.source.split())
        hashed = md5(
            f"{self.name}:{self.path}:{normalized_source}".encode()
        ).hexdigest()
        return hashed[:7]

    @property
    def nodelist(self):
        return self.template.template.nodelist

    @property
    def path(self):
        return self.template.template.origin.name

    @property
    def source(self):
        return self.template.template.source

    @classmethod
    def from_abs_path(cls, path: Path) -> Component:
        template = select_template([str(path)])
        return cls.from_template(template)

    @classmethod
    def from_name(cls, name: str) -> Component:
        template_names = get_template_names(name)
        template = select_template(template_names)
        return cls.from_template(template)

    @classmethod
    def from_template(cls, template: DjangoTemplate) -> Component:
        template_path = Path(template.template.origin.name)

        for component_dir in get_component_directories():
            try:
                relative_path = template_path.relative_to(component_dir)
                name = str(relative_path.with_suffix("")).replace("/", ".")
                break
            except ValueError:
                continue
        else:
            name = template_path.stem

        assets: list[Iterable[Asset]] = pm.hook.collect_component_assets(
            template_path=Path(template.template.origin.name)
        )

        return cls(
            name=name, template=template, assets=frozenset(itertools.chain(*assets))
        )


class SequenceGenerator:
    _instance: SequenceGenerator | None = None
    _lock: Lock = Lock()
    _counters: dict[str, int]

    def __init__(self) -> None:
        if not hasattr(self, "_counters"):
            self._counters = {}

    def __new__(cls) -> SequenceGenerator:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def next(self, component: Component) -> int:
        with self._lock:
            current = self._counters.get(component.id, 0) + 1
            self._counters[component.id] = current
        return current


@dataclass
class BoundComponent:
    component: Component
    params: Params
    nodelist: NodeList | None
    _sequence: SequenceGenerator = field(default_factory=SequenceGenerator)

    def render(self, context: Context):
        if app_settings.ENABLE_BIRD_ATTRS:
            data_attrs = [
                Param(
                    f"data-bird-{self.component.data_attribute_name}",
                    Value(True),
                ),
                Param("data-bird-id", Value(f'"{self.component.id}-{self.id}"')),
            ]
            self.params.attrs.extend(data_attrs)

        props = self.params.render_props(self.component, context)
        attrs = self.params.render_attrs(context)
        slots = self.fill_slots(context)

        with context.push(
            **{
                "attrs": attrs,
                "props": props,
                "slot": slots.get(DEFAULT_SLOT),
                "slots": slots,
                "vars": {},
            }
        ):
            return self.component.template.template.render(context)

    def fill_slots(self, context: Context):
        if self.nodelist is None:
            return {
                DEFAULT_SLOT: None,
            }

        slot_nodes = {
            node.name: node for node in self.nodelist if isinstance(node, SlotNode)
        }
        default_nodes = NodeList(
            [node for node in self.nodelist if not isinstance(node, SlotNode)]
        )

        slots: dict[str, Node | NodeList] = {
            DEFAULT_SLOT: default_nodes,
            **slot_nodes,
        }

        if not slots[DEFAULT_SLOT] and "slot" in context:
            slots[DEFAULT_SLOT] = TextNode(context["slot"])

        return {name: node.render(context) for name, node in slots.items() if node}

    @property
    def id(self):
        return str(self._sequence.next(self.component))


class ComponentRegistry:
    def __init__(self):
        self._component_usage: dict[str, set[Path]] = defaultdict(set)
        self._components: dict[str, Component] = {}
        self._template_usage: dict[Path, set[str]] = defaultdict(set)

    def reset(self) -> None:
        """Reset the registry, used for testing."""
        self._component_usage = defaultdict(set)
        self._components = {}
        self._template_usage = defaultdict(set)

    def get_assets(self, asset_type: AssetType | None = None) -> frozenset[Asset]:
        return frozenset(
            asset
            for component in self._components.values()
            for asset in component.assets
            if asset_type is None or asset.type == asset_type
        )

    def get_component(self, name: str) -> Component:
        if name in self._components and not settings.DEBUG:
            return self._components[name]

        self._components[name] = Component.from_name(name)
        if name not in self._component_usage:
            self._component_usage[name] = set()
        return self._components[name]

    def get_component_names_used_in_template(
        self, template_path: str | Path
    ) -> set[str]:
        """Get names of components used in a template."""

        path = Path(template_path)

        if path in self._template_usage:
            return self._template_usage[path]

        components = find_components_in_template(template_path)

        self._template_usage[path] = components
        for component_name in components:
            self._component_usage[component_name].add(path)

        return components

    def get_component_usage(
        self, template_path: str | Path
    ) -> Generator[Component, Any, None]:
        """Get components used in a template."""
        for component_name in self.get_component_names_used_in_template(template_path):
            yield Component.from_name(component_name)


components = ComponentRegistry()
