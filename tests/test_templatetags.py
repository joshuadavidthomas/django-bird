from __future__ import annotations

import re

import pytest
from django.template import Context
from django.template import Template


@pytest.mark.parametrize(
    "contents,expected",
    [
        (
            "{% bird_component button %}Click me{% endbird_component %}",
            "<button>Click me</button>",
        ),
        (
            "{% bird_component 'button' %}Click me{% endbird_component %}",
            "<button>Click me</button>",
        ),
        (
            '{% bird_component "button" %}Click me{% endbird_component %}',
            "<button>Click me</button>",
        ),
        (
            "{% bird_component button class='btn' %}Click me{% endbird_component %}",
            "<button class='btn'>Click me</button>",
        ),
    ],
)
def test_bird_component_templatetag(contents, expected):
    template = Template(contents)

    rendered = template.render(context=Context({}))
    # normalize all whitespace
    rendered = re.sub(r"\s+", " ", rendered)
    rendered = re.sub(r">\s+", ">", rendered)
    rendered = re.sub(r"\s+<", "<", rendered)
    rendered = rendered.strip()

    assert rendered == expected


@pytest.mark.parametrize(
    "contents,expected",
    [
        ("{{ slot }}", "test"),
        ("{% slot %}{% endslot %}", "test"),
        ("{% slot default %}{% endslot %}", "test"),
        ("{% slot 'default' %}{% endslot %}", "test"),
        ('{% slot "default" %}{% endslot %}', "test"),
        ("{% slot name='default' %}{% endslot %}", "test"),
        ('{% slot name="default" %}{% endslot %}', "test"),
        ("{% slot name='not-default' %}{% endslot %}", ""),
    ],
)
def test_slot_templatetag(contents, expected):
    template = Template(contents)

    rendered = template.render(
        context=Context({"slot": "test", "slots": {"default": "test"}})
    )

    assert rendered == expected
