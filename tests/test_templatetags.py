from __future__ import annotations

import re

import pytest
from django.template import Context
from django.template import Template


class TestBirdComponentTemplatetag:
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
        ],
    )
    def test_component_name(self, contents, expected):
        template = Template(contents)

        rendered = template.render(context=Context({}))

        assert self.normalize_whitespace(rendered) == expected

    @pytest.mark.parametrize(
        "contents,expected",
        [
            (
                "{% bird_component button class='btn' %}Click me{% endbird_component %}",
                '<button class="btn">Click me</button>',
            ),
        ],
    )
    def test_attrs(self, contents, expected):
        template = Template(contents)

        rendered = template.render(context=Context({}))

        assert self.normalize_whitespace(rendered) == expected

    def normalize_whitespace(self, text):
        # this makes writing tests much easier, as it gets rid of any
        # existing whitespace that may be present in the template file

        # multiple whitespace characters
        text = re.sub(r"\s+", " ", text)

        # after opening tag, including when there are attributes
        text = re.sub(r"<(\w+)(\s+[^>]*)?\s*>", r"<\1\2>", text)

        # before closing tag
        text = re.sub(r"\s+>", ">", text)

        # after opening tag and before closing tag
        text = re.sub(r">\s+<", "><", text)

        # immediately after opening tag (including attributes) or before closing tag
        text = re.sub(r"(<\w+(?:\s+[^>]*)?>)\s+|\s+(<\/\w+>)", r"\1\2", text)

        return text.strip()

    @pytest.mark.parametrize(
        "contents,expected",
        [
            ("<button> Click me </button>", "<button>Click me</button>"),
            ("<button> Click me</button>", "<button>Click me</button>"),
            ("<button>Click me </button>", "<button>Click me</button>"),
            ("<button >Click me</button>", "<button>Click me</button>"),
            (
                "<button class='btn'> Click me </button>",
                "<button class='btn'>Click me</button>",
            ),
            ("\n<button>\n  Click me\n</button>\n", "<button>Click me</button>"),
        ],
    )
    def test_normalize_whitespace(self, contents, expected):
        assert self.normalize_whitespace(contents) == expected


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
