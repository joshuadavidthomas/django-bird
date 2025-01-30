from __future__ import annotations

from collections import defaultdict
from collections.abc import Generator
from dataclasses import dataclass
from dataclasses import field
from hashlib import md5
from pathlib import Path
from threading import Lock
from typing import Any

from cachetools import LRUCache
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
from .staticfiles import Asset
from .staticfiles import AssetType
from .templates import gather_bird_tag_template_usage
from .templates import get_component_directories
from .templates import get_template_names
from .templates import scan_template_for_bird_tag
from .templatetags.tags.bird import BirdNode
from .templatetags.tags.slot import DEFAULT_SLOT
from .templatetags.tags.slot import SlotNode
from .utils import get_files_from_dirs


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
        params = Params.with_attrs(node.attrs)
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

    @property
    def used_in(self):
        return components.get_template_usage(self.name)

    @classmethod
    def from_abs_path(cls, path: Path, root: Path) -> Component | None:
        name = str(path.relative_to(root).with_suffix("")).replace("/", ".")
        return cls.from_name(name)

    @classmethod
    def from_name(cls, name: str):
        template_names = get_template_names(name)
        template = select_template(template_names)
        assets: list[Asset] = [
            asset
            for asset_type in AssetType
            if (
                asset := Asset.from_path(
                    Path(template.template.origin.name), asset_type
                )
            )
            is not None
        ]
        return cls(name=name, template=template, assets=frozenset(assets))


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
                    Value(True, False),
                ),
                Param("data-bird-id", Value(f"{self.component.id}-{self.id}", True)),
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

        if context.get("slots"):
            for name, content in context["slots"].items():
                if name not in slots or not slots.get(name):
                    slots[name] = TextNode(str(content))

        if not slots[DEFAULT_SLOT] and "slot" in context:
            slots[DEFAULT_SLOT] = TextNode(context["slot"])

        return {name: node.render(context) for name, node in slots.items() if node}

    @property
    def id(self):
        return str(self._sequence.next(self.component))


class ComponentRegistry:
    def __init__(self, maxsize: int = 100):
        self._component_usage: dict[str, set[Path]] = defaultdict(set)
        self._components: LRUCache[str, Component] = LRUCache(maxsize=maxsize)
        self._template_usage: dict[Path, set[str]] = defaultdict(set)

    def discover_components(self) -> None:
        component_dirs = get_component_directories()
        component_paths = get_files_from_dirs(component_dirs)
        for component_abs_path, root_abs_path in component_paths:
            if component_abs_path.suffix != ".html":
                continue

            component = Component.from_abs_path(component_abs_path, root_abs_path)
            if component is None:
                continue

            if component.name not in self._components:
                self._components[component.name] = component

        templates_using_bird_tag = gather_bird_tag_template_usage()
        for template_abs_path, root_abs_path in templates_using_bird_tag:
            if self._template_usage.get(template_abs_path, None) is not None:
                continue

            template_name = template_abs_path.relative_to(root_abs_path)
            for component_name in scan_template_for_bird_tag(str(template_name)):
                self._template_usage[template_abs_path].add(component_name)
                self._component_usage[component_name].add(template_abs_path)

    def reset(self) -> None:
        """Reset the registry, used for testing."""
        self._component_usage = defaultdict(set)
        self._components.clear()
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

    def get_component_usage(
        self, template_path: str | Path
    ) -> Generator[Component, Any, None]:
        path = Path(template_path) if isinstance(template_path, str) else template_path
        for component_name in self._template_usage.get(path, set()):
            yield Component.from_name(component_name)

    def get_template_usage(self, component: str | Component) -> frozenset[Path]:
        name = component.name if isinstance(component, Component) else component
        return frozenset(self._component_usage.get(name, set()))


components = ComponentRegistry()
