from __future__ import annotations

from http import HTTPStatus

import pytest
from django.http.response import Http404
from django.test import override_settings

from django_bird.staticfiles import AssetType
from django_bird.views import asset_view

from .utils import TestAsset
from .utils import TestComponent


@pytest.fixture(autouse=True)
def debug_mode():
    with override_settings(DEBUG=True):
        yield


def test_asset_view_css(templates_dir, rf):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()

    request = rf.get("/assets/")
    response = asset_view(request, button.name, button_css.file.name)

    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "text/css"


def test_asset_view_js(templates_dir, rf):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_js = TestAsset(
        component=button, content="console.log('button');", asset_type=AssetType.JS
    ).create()

    request = rf.get("/assets/")
    response = asset_view(request, button.name, button_js.file.name)

    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "application/javascript"


def test_asset_view_invalid_type(templates_dir, rf):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )

    button_txt_file = button.file.parent / f"{button.file.stem}.txt"
    button_txt_file.write_text("hello from a text file")

    request = rf.get("/assets/")

    with pytest.raises(Http404):
        asset_view(request, button.name, button_txt_file.name)


def test_asset_view_nonexistent_component(templates_dir, rf):
    bird_dir = templates_dir / "bird"
    bird_dir.mkdir(exist_ok=True)

    nonexistent_css_file = bird_dir / "nonexistent.css"
    nonexistent_css_file.write_text(".button { color: blue; }")

    request = rf.get("/assets/")

    with pytest.raises(Http404):
        asset_view(request, "nonexistent", nonexistent_css_file.name)


def test_asset_view_nonexistent_asset(templates_dir, rf):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )

    request = rf.get("/assets/")

    with pytest.raises(Http404):
        asset_view(request, button.name, "button.css")
