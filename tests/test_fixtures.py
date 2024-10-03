from __future__ import annotations

import pytest
from django.template.loader import get_template


def test_create_bird_template(create_bird_template):
    name = "foo"
    content = "<div>bar</div>"

    create_bird_template(name, content)

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
