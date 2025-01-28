from __future__ import annotations

from http import HTTPStatus

import pytest
from django.test import override_settings
from django.urls import reverse

from django_bird.staticfiles import AssetType

from .utils import TestAsset
from .utils import TestComponent

pytestmark = [
    pytest.mark.filterwarnings(
        "ignore:The 'asset_view' is deprecated.*:DeprecationWarning"
    ),
]


@pytest.fixture(autouse=True)
def debug_mode():
    with override_settings(DEBUG=True):
        yield


def test_url_reverse(templates_dir):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()

    assert reverse(
        "django_bird:asset",
        kwargs={"component_name": button.name, "asset_filename": button_css.file.name},
    )


def test_get_css(templates_dir, client):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()

    response = client.get(f"/__bird__/assets/{button.name}/{button_css.file.name}")

    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "text/css"

    content = b"".join(response.streaming_content).decode()

    assert content == ".button { color: blue; }"


def test_get_js(templates_dir, client):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_js = TestAsset(
        component=button, content="console.log('button');", asset_type=AssetType.JS
    ).create()

    response = client.get(f"/__bird__/assets/{button.name}/{button_js.file.name}")

    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "application/javascript"

    content = b"".join(response.streaming_content).decode()

    assert content == "console.log('button');"


def test_get_invalid_type(templates_dir, client):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )

    button_txt_file = button.file.parent / f"{button.file.stem}.txt"
    button_txt_file.write_text("hello from a text file")

    response = client.get(f"/__bird__/assets/{button.name}/{button_txt_file.name}")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_nonexistent_component(templates_dir, client):
    bird_dir = templates_dir / "bird"
    bird_dir.mkdir(exist_ok=True)

    nonexistent_css_file = bird_dir / "nonexistent.css"
    nonexistent_css_file.write_text(".button { color: blue; }")

    response = client.get(f"/__bird__/assets/nonexistent/{nonexistent_css_file.name}")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_asset_view_nonexistent_asset(templates_dir, client):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )

    response = client.get(f"/__bird__/assets/{button.name}/button.css")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_asset_view_warns_debug_false(templates_dir, client):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )
    button_css = TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()

    with override_settings(DEBUG=False):
        with pytest.warns(RuntimeWarning):
            response = client.get(
                f"/__bird__/assets/{button.name}/{button_css.file.name}"
            )

    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "text/css"
