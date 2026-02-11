from __future__ import annotations

import pytest
from django import template
from django.template import Context
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType

from django_bird.templatetags.tags.load import TAG
from django_bird.templatetags.tags.load import do_load


@pytest.mark.parametrize(
    "contents,expected",
    [
        ("button", ["button"]),
        ("button modal.trigger", ["button", "modal.trigger"]),
        ("'button' \"modal.trigger\"", ["button", "modal.trigger"]),
    ],
)
def test_do_load(contents, expected):
    token = Token(TokenType.BLOCK, f"{TAG} {contents}")

    node = do_load(Parser([]), token)

    assert node.component_names == expected


def test_do_load_no_args():
    token = Token(TokenType.BLOCK, TAG)

    with pytest.raises(template.TemplateSyntaxError):
        do_load(Parser([]), token)


def test_load_node_renders_empty_string():
    token = Token(TokenType.BLOCK, f"{TAG} button")
    node = do_load(Parser([]), token)

    assert node.render(Context({})) == ""
