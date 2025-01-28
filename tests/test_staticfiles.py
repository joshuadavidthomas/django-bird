from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.template.base import Template
from django.template.context import Context
from django.test import override_settings

from django_bird.components import Component
from django_bird.conf import DJANGO_BIRD_FINDER
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
from django_bird.staticfiles import BirdAssetFinder

from .utils import TestAsset
from .utils import TestComponent


class TestAssetClass:
    def test_hash(self):
        asset1 = Asset(Path("static.css"), AssetType.CSS)
        asset2 = Asset(Path("static.css"), AssetType.CSS)

        assert asset1 == asset2
        assert hash(asset1) == hash(asset2)

        assets = {asset1, asset2, Asset(Path("other.css"), AssetType.CSS)}

        assert len(assets) == 2

    def test_exists(self, tmp_path: Path):
        css_file = tmp_path / "test.css"
        css_file.touch()

        asset = Asset(css_file, AssetType.CSS)

        assert asset.exists() is True

    def test_exists_nonexistent(self):
        missing_asset = Asset(Path("missing.css"), AssetType.CSS)

        assert missing_asset.exists() is False

    @pytest.mark.parametrize(
        "asset,expected_html_tag_bits",
        [
            (Asset(Path("static.css"), AssetType.CSS), 'link rel="stylesheet" href='),
            (Asset(Path("static.js"), AssetType.JS), "script src="),
        ],
    )
    def test_render(self, asset, expected_html_tag_bits):
        rendered = asset.render()

        assert expected_html_tag_bits in rendered
        assert asset.url in rendered

    def test_storage(self, templates_dir, settings):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(button.name)
        asset = component.get_asset(button_css.file.name)

        assert str(asset.storage.location) in str(button_css.file)

    def test_template_dir(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(button.name)
        asset = component.get_asset(button_css.file.name)

        assert asset.template_dir == templates_dir

    def test_template_dir_nested(self, templates_dir):
        button = TestComponent(
            name="button",
            content="<button>Click me</button>",
            sub_dir="nested",
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(f"{button.sub_dir}.{button.name}")
        asset = component.get_asset(button_css.file.name)

        assert asset.template_dir == templates_dir

    def test_relative_path(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(button.name)
        asset = component.get_asset(button_css.file.name)

        assert asset.relative_path == Path("bird/button.css")

    def test_relative_path_nested(self, templates_dir):
        button = TestComponent(
            name="button",
            content="<button>Click me</button>",
            sub_dir="nested",
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(f"{button.sub_dir}.{button.name}")
        asset = component.get_asset(button_css.file.name)

        assert asset.relative_path == Path("bird/nested/button.css")

    def test_url_with_staticfiles_finder(self, templates_dir):
        button = TestComponent(
            name="button",
            content="<button>Click me</button>",
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(button.name)
        asset = component.get_asset(button_css.file.name)

        assert asset.url == str(button_css.file)

    def test_url_with_reverse_fallback(self, templates_dir):
        button = TestComponent(
            name="button",
            content="<button>Click me</button>",
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        component = Component.from_name(button.name)
        asset = component.get_asset(button_css.file.name)

        with override_settings(
            STATICFILES_FINDERS=[
                finder
                for finder in settings.STATICFILES_FINDERS
                if finder != DJANGO_BIRD_FINDER
            ]
        ):
            assert asset.url == f"/__bird__/assets/{component.name}/{asset.path.name}"

    def test_from_path(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

        assert Asset.from_path(button.file, button_css.asset_type) == Asset(
            button_css.file, button_css.asset_type
        )
        assert Asset.from_path(button.file, button_js.asset_type) == Asset(
            button_js.file, button_js.asset_type
        )

    def test_from_template_nested(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>", sub_dir="nested"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        assert Asset.from_path(button.file, button_css.asset_type) == Asset(
            button_css.file, button_css.asset_type
        )


class TestBirdAssetFinder:
    def test_check(self):
        finder = BirdAssetFinder()

        assert finder.check() == []

    def test_list_all_assets(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        input = TestComponent(name="input", content="<input>").create(templates_dir)

        assets = [
            TestAsset(
                component=button,
                content=".button { color: blue; }",
                asset_type=AssetType.CSS,
            ).create(),
            TestAsset(
                component=button,
                content="console.log('button');",
                asset_type=AssetType.JS,
            ).create(),
            TestAsset(
                component=input,
                content="input { border: 1px solid black; }",
                asset_type=AssetType.CSS,
            ).create(),
            TestAsset(
                component=input,
                content="console.log('input');",
                asset_type=AssetType.JS,
            ).create(),
        ]

        finder = BirdAssetFinder()
        listed_assets = list(finder.list(None))

        assert len(listed_assets) == len(assets)

        for asset in assets:
            assert any(
                asset.file.name in relative_path for relative_path, _ in listed_assets
            )

    def test_list_ignore(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        finder = BirdAssetFinder()

        assert len(list(finder.list(["bird/*"]))) == 0
        assert len(list(finder.list(["*/button*"]))) == 0
        assert len(list(finder.list(["*.css"]))) == 0

    def test_list_custom_dir(self, templates_dir, override_app_settings):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        custom_button = TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        custom_button_css = TestAsset(
            component=custom_button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        finder = BirdAssetFinder()

        with override_app_settings(COMPONENT_DIRS=["components"]):
            listed_assets = list(finder.list(None))

        assert len(listed_assets) == 1
        # components are matched like templates, dirs in
        # `settings.DJANGO_BIRD["COMPONENT_DIRS"]` take precedence
        assert listed_assets[0][0] in str(custom_button_css.file)
        assert listed_assets[0][0] not in str(button_css.file)


class TestFindersFind:
    def test_find_asset(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

        assert finders.find("bird/button.css") == str(button_css.file)
        assert finders.find("bird/button.js") == str(button_js.file)

    def test_find_asset_custom_dir(self, templates_dir, override_app_settings):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        custom_button = TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        custom_button_css = TestAsset(
            component=custom_button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        with override_app_settings(COMPONENT_DIRS=["components"]):
            # components are matched like templates, dirs in
            # `settings.DJANGO_BIRD["COMPONENT_DIRS"]` take precedence
            assert finders.find("components/button.css") == str(custom_button_css.file)
            assert finders.find("bird/button.css") is None

    def test_find_nested_asset(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>", sub_dir="nested"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        assert finders.find("bird/nested/button.css") == str(button_css.file)

    def test_case_sensitive_component_names(self, templates_dir):
        component = TestComponent(name="Button", content="<button>").create(
            templates_dir
        )
        TestAsset(component=component, content="", asset_type=AssetType.CSS).create()

        assert finders.find("bird/Button.css") is not None
        assert finders.find("bird/button.css") is None

    def test_find_intermediate_paths(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>", sub_dir="nested"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        assert finders.find("bird/") is not None
        assert finders.find("bird/nested/") is not None
        assert finders.find("bird/nested/button.css") is not None

    def test_find_component_template(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        assert finders.find("bird/button.html") is None

    def test_find_nonexistent(self):
        assert finders.find("bird/nonexistent.js") is None

    def test_find_all(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        assert finders.find("bird/button.css", all=True) == [str(button_css.file)]


class TestStaticCollection:
    @pytest.fixture(autouse=True)
    def staticfiles_app(self):
        with override_settings(
            INSTALLED_APPS=settings.INSTALLED_APPS + ["django.contrib.staticfiles"],
            STATIC_URL="/static/",
        ):
            yield

    @pytest.fixture
    def static_root(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        with override_settings(STATIC_ROOT=str(static_dir)):
            yield static_dir

        shutil.rmtree(static_dir)

    def test_basic(self, templates_dir, static_root):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        TestAsset(
            component=button,
            content="console.log('button');",
            asset_type=AssetType.JS,
        ).create()

        call_command("collectstatic", interactive=False, verbosity=0)

        assert (static_root / "django_bird/bird/button.css").exists()
        assert (static_root / "django_bird/bird/button.js").exists()

    def test_custom_dir(self, templates_dir, static_root, override_app_settings):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        custom_button = TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        TestAsset(
            component=custom_button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        with override_app_settings(COMPONENT_DIRS=["components"]):
            call_command("collectstatic", interactive=False, verbosity=0)

            # components are matched like templates, dirs in
            # `settings.DJANGO_BIRD["COMPONENT_DIRS"]` take precedence
            assert (static_root / "django_bird/components/button.css").exists()
            assert not (static_root / "django_bird/bird/button.css").exists()

    def test_same_named_assets(self, templates_dir, static_root):
        button1 = TestComponent(
            name="button", content="<button>Form Button</button>", sub_dir="forms"
        ).create(templates_dir)
        button2 = TestComponent(
            name="button", content="<button>Nav Button</button>", sub_dir="nav"
        ).create(templates_dir)

        button1_css = TestAsset(
            component=button1,
            content=".form-button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button2_css = TestAsset(
            component=button2,
            content=".nav-button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()

        call_command("collectstatic", interactive=False, verbosity=0)

        form_css = static_root / "django_bird/bird/forms/button.css"
        nav_css = static_root / "django_bird/bird/nav/button.css"

        assert form_css.exists()
        assert nav_css.exists()
        assert form_css.read_text() == button1_css.content
        assert nav_css.read_text() == button2_css.content
        assert form_css.read_text() != button2_css.content
        assert nav_css.read_text() != button1_css.content

    def test_dry_run_collection(self, templates_dir, static_root):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        call_command("collectstatic", interactive=False, dry_run=True, verbosity=0)

        assert not (static_root / "bird").exists()

    def test_clear_collection(self, templates_dir, static_root):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        call_command("collectstatic", interactive=False, verbosity=0)

        assert (static_root / "django_bird/bird/button.css").exists()
        assert not (static_root / "django_bird/bird/input.css").exists()

        input = TestComponent(name="input", content="<input>").create(templates_dir)
        TestAsset(
            component=input,
            content="input { border: 1px solid black; }",
            asset_type=AssetType.CSS,
        ).create()

        call_command("collectstatic", interactive=False, clear=True, verbosity=0)

        assert (static_root / "django_bird/bird/button.css").exists()
        assert (static_root / "django_bird/bird/input.css").exists()


class TestStaticTemplateTag:
    @pytest.fixture(autouse=True)
    def staticfiles_app(self):
        with override_settings(
            INSTALLED_APPS=settings.INSTALLED_APPS + ["django.contrib.staticfiles"],
            STATIC_URL="/static/",
        ):
            yield

    def test_static_tag(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        template = Template(
            '{% load static %}{% static "django_bird/bird/button.css" %}'
        )
        rendered = template.render(Context({}))

        assert rendered == "/static/django_bird/bird/button.css"

    def test_static_tag_nonexistent_asset(self):
        template = Template(
            '{% load static %}{% static "django_bird/bird/nonexistent.css" %}'
        )
        rendered = template.render(Context({}))

        assert rendered == "/static/django_bird/bird/nonexistent.css"
