from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from cachetools import LRUCache
from django.apps import apps
from django.conf import settings
from django.template.backends.django import Template as DjangoTemplate
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import select_template

from django_bird.staticfiles import Asset

from .conf import app_settings
from .staticfiles import AssetType
from .templates import get_template_names


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    template: DjangoTemplate
    assets: frozenset[Asset] = field(default_factory=frozenset)

    def render(self, context: dict[str, Any]):
        return self.template.render(context)

    @property
    def nodelist(self):
        return self.template.template.nodelist

    @classmethod
    def from_name(cls, name: str):
        template_names = get_template_names(name)
        template = select_template(template_names)

        assets: set[Asset] = set()
        template_path = Path(template.template.origin.name)
        for asset_type in AssetType:
            asset_path = template_path.with_suffix(asset_type.ext)
            if asset_path.exists():
                asset = Asset.from_path(asset_path)
                assets.add(asset)

        return cls(name=name, template=template, assets=frozenset(assets))


class ComponentRegistry:
    def __init__(self, maxsize: int = 100):
        self._components: LRUCache[str, Component] = LRUCache(maxsize=maxsize)

    def get_dirs(self):
        engine = Engine.get_default()
        dirs: list[str | Path] = list(engine.dirs)

        for app_config in apps.get_app_configs():
            template_dir = Path(app_config.path) / "templates"
            if template_dir.is_dir():
                dirs.append(template_dir)

        base_dir = getattr(settings, "BASE_DIR", None)

        if base_dir is not None:
            root_template_dir = Path(base_dir) / "templates"
            if root_template_dir.is_dir():
                dirs.append(root_template_dir)

        return dirs

    def discover_components(self) -> None:
        template_dirs = self.get_dirs()

        component_dirs = [
            Path(template_dir) / component_dir
            for template_dir in template_dirs
            for component_dir in app_settings.COMPONENT_DIRS + ["bird"]
        ]

        for component_dir in component_dirs:
            component_dir = Path(component_dir)

            if not component_dir.is_dir():
                continue

            for component_path in component_dir.rglob("*.html"):
                component_name = str(
                    component_path.relative_to(component_dir).with_suffix("")
                )
                try:
                    self.get_component(component_name)
                except TemplateDoesNotExist:
                    continue

    def clear(self) -> None:
        """Clear the registry. Mainly useful for testing."""
        self._components.clear()

    def get_component(self, name: str) -> Component:
        try:
            return self._components[name]
        except KeyError:
            component = Component.from_name(name)
            if not settings.DEBUG:
                self._components[name] = component
            return component

    def get_assets(self, asset_type: AssetType) -> list[Asset]:
        assets: list[Asset] = []
        for component in self._components.values():
            assets.extend(a for a in component.assets if a.type == asset_type)
        return assets


components = ComponentRegistry()
