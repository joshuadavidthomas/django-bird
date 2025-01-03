from __future__ import annotations

import pytest
from django.template.loader import get_template

from .utils import TestComponent


def test_test_component(templates_dir):
    name = "foo"
    content = "<div>bar</div>"

    TestComponent(name=name, content=content).create(templates_dir)

    template = get_template(f"bird/{name}.html")

    assert template
    assert template.render({}) == content


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
def test_normalize_whitespace(contents, expected, normalize_whitespace):
    assert normalize_whitespace(contents) == expected
