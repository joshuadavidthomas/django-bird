from __future__ import annotations

from django_bird.plugins.file_assets import find_component_asset
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
from tests.utils import TestAsset
from tests.utils import TestComponent


def test_find_component_asset(templates_dir):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()
    button_js = TestAsset(
        component=button, content="console.log('button');", asset_type=AssetType.JS
    ).create()

    assert find_component_asset(button.file, button_css.asset_type) == Asset(
        button_css.file, button_css.asset_type
    )
    assert find_component_asset(button.file, button_js.asset_type) == Asset(
        button_js.file, button_js.asset_type
    )


def test_from_template_nested(templates_dir):
    button = TestComponent(
        name="button", content="<button>Click me</button>", sub_dir="nested"
    ).create(templates_dir)
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()

    assert find_component_asset(button.file, button_css.asset_type) == Asset(
        button_css.file, button_css.asset_type
    )
