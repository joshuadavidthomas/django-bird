from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from django.template.backends.django import Template
from django.template.loader import select_template

from .templates import get_template_names

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    template: Template

    def render(self, context: dict[str, Any]):
        return self.template.render(context)

    @property
    def nodelist(self):
        return self.template.template.nodelist

    @classmethod
    def from_name(cls, name: str):
        template_names = get_template_names(name)
        template = select_template(template_names)
        return cls(name=name, template=template)
