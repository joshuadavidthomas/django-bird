from __future__ import annotations

from django.template.loader import get_template


def test_template_inheritance_assets(example_template):
    rendered = get_template(example_template.template.name).render({})

    assert all(
        asset.url in rendered
        for component in example_template.used_components
        for asset in component.assets
    )
    assert not any(
        asset.url in rendered
        for component in example_template.unused_components
        for asset in component.assets
    )
