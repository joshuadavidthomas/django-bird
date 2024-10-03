from __future__ import annotations

from typing import Any

Component = Any


class BirdComponentRegistry:
    def __init__(self) -> None:
        self.components: dict[str, Component] = {}

    def get(self, tag_name: str) -> Component | None:
        return self.components.get(tag_name)

    def __getitem__(self, tag_name: str) -> Component | None:
        return self.get(tag_name)

    def register(self, tag_name: str, component: Component) -> None:
        self.components[tag_name] = component

    def __setitem__(self, tag_name: str, component: Component) -> None:
        self.register(tag_name, component)
