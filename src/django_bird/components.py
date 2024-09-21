from __future__ import annotations

from typing import Protocol
from typing import runtime_checkable


class BirdTransformer:
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

    def transform(self, tag_name: str, attrs: str, content: str) -> str:
        component = self.get(tag_name)

        if component:
            attr_dict = {}
            for attr in attrs.split():
                if "=" in attr:
                    key, value = attr.split("=", 1)
                    value = value.strip("'\"")
                else:
                    key, value = attr, ""
                attr_dict[key] = value
            transformed = component.transform(attr_dict, content)
        else:
            transformed = f"<div {attrs.strip()}>{content}</div>"

        return transformed


transformer = BirdTransformer()


@runtime_checkable
class Component(Protocol):
    def transform(self, attrs: dict[str, str], content: str) -> str: ...


class ButtonComponent:
    TEMPLATE = '{{% load django_bootstrap5 %}}{{% bootstrap_button "{content}" button_class="{classes}" %}}'

    def transform(self, attrs: dict[str, str], content: str) -> str:
        classes = attrs.get("class", "")
        return self.TEMPLATE.format(content=content, classes=classes)


transformer.register("button", ButtonComponent())
