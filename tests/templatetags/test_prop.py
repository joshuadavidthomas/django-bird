from __future__ import annotations

import pytest
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType

from django_bird.templatetags.tags.prop import TAG
from django_bird.templatetags.tags.prop import do_prop


@pytest.mark.parametrize(
    "prop,expected",
    [
        ("id", ("id", None, [])),
        ("class='btn'", ("class", "'btn'", [])),
    ],
)
def test_do_prop(prop, expected):
    start_token = Token(TokenType.BLOCK, f"{TAG} {prop}")

    node = do_prop(Parser([]), start_token)

    assert node.name == expected[0]
    assert node.default == expected[1]
    assert node.attrs == expected[2]
