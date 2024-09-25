from __future__ import annotations

import pytest
from django.template.loader import get_template


@pytest.mark.parametrize(
    "template_name",
    (
        "with_bird.html",
        "without_bird.html",
    ),
)
def test_render_template(template_name):
    context = {
        "title": "Test Title",
        "content": "Test Content",
    }

    template = get_template(template_name)
    rendered = template.render(context)

    assert rendered
