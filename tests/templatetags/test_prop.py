from __future__ import annotations

import pytest
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType

from django_bird.templatetags.tags.prop import TAG
from django_bird.templatetags.tags.prop import PropNode
from django_bird.templatetags.tags.prop import do_prop


@pytest.mark.parametrize(
    "contents,expected",
    [
        ("id", PropNode(name="id", default=None, attrs=[])),
        ("class='btn'", PropNode(name="class", default="'btn'", attrs=[])),
    ],
)
def test_do_prop(contents, expected):
    start_token = Token(TokenType.BLOCK, f"{TAG} {contents}")

    node = do_prop(Parser([]), start_token)

    assert node.name == expected.name
    assert node.default == expected.default
    assert node.attrs == expected.attrs
