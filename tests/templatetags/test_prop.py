from __future__ import annotations

import pytest
from django.template.exceptions import TemplateSyntaxError

from django_bird.templatetags.tags.prop import parse_prop_name


@pytest.mark.parametrize(
    "bits,expected",
    [
        (["bird:prop", "id"], ("id", None)),
        (["bird:prop", "class='btn'", "foo"], ("class", "btn")),
    ],
)
def test_parse_prop_name(bits, expected):
    assert parse_prop_name(bits) == expected


def test_parse_prop_name_no_args():
    with pytest.raises(TemplateSyntaxError):
        parse_prop_name([])
