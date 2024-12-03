from __future__ import annotations

import pytest
from django.template.backends.django import Template

from django_bird.components import Component
from django_bird.components import Registry


class TestComponent:
    def test_from_name(self, create_bird_template):
        create_bird_template("button", "<button>Click me</button>")

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert isinstance(comp.template, Template)
        assert comp.render({}) == "<button>Click me</button>"


class TestRegistry:
    @pytest.fixture
    def registry(self):
        return Registry(maxsize=2)

    def test_get_component_caches(self, registry, create_bird_template):
        create_bird_template(name="button", content="<button>Click me</button>")

        component1 = registry.get_component("button")
        component2 = registry.get_component("button")

        assert component1 is component2

    def test_lru_cache_behavior(self, registry, create_bird_template):
        create_bird_template(name="button1", content="1")
        create_bird_template(name="button2", content="2")
        create_bird_template(name="button3", content="3")

        button1 = registry.get_component("button1")
        button2 = registry.get_component("button2")
        button3 = registry.get_component("button3")

        new_button1 = registry.get_component("button1")
        assert new_button1 is not button1

        cached_button2 = registry.get_component("button2")
        assert cached_button2.name == button2.name
        assert cached_button2.render({}) == button2.render({})

        cached_button3 = registry.get_component("button3")
        assert cached_button3.name == button3.name
        assert cached_button3.render({}) == button3.render({})

    def test_clear_cache(self, registry, create_bird_template):
        create_bird_template(name="button", content="<button>Click me</button>")

        component1 = registry.get_component("button")
        registry.clear()
        component2 = registry.get_component("button")

        assert component1 is not component2

    def test_component_not_found(self, registry):
        with pytest.raises(Exception):
            registry.get_component("nonexistent")
