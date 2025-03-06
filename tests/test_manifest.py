from __future__ import annotations

import json
import shutil
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings

from django_bird.manifest import default_manifest_path
from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import load_asset_manifest
from django_bird.manifest import save_asset_manifest
from tests.utils import TestComponent


@pytest.fixture(autouse=True)
def reset_manifest_cache():
    # Access and reset the private module-level cache variable
    import django_bird.manifest

    django_bird.manifest._manifest_cache = None
    yield
    django_bird.manifest._manifest_cache = None


@pytest.fixture
def static_root(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()

    with override_settings(STATIC_ROOT=str(static_dir)):
        yield static_dir

    shutil.rmtree(static_dir)


def test_load_asset_manifest_nonexistent():
    with override_settings(STATIC_ROOT="/nonexistent/path/"):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_invalid_json(static_root):
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "manifest.json"
    manifest_path.write_text("{ this is not valid JSON }")

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest is None


def test_load_asset_manifest_permission_error(static_root, monkeypatch):
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "manifest.json"
    manifest_path.write_text("{}")

    # Mock open to raise a permission error
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise PermissionError("Permission denied")
        return open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_with_error)

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest is None


def test_load_asset_manifest_os_error(static_root, monkeypatch):
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "asset-manifest.json"
    manifest_path.write_text("{}")

    # Mock open to raise an OS error
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise OSError("I/O error")
        return open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_with_error)

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest is None


def test_load_asset_manifest_from_static_root(static_root):
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(test_manifest_data, f)

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest == test_manifest_data


def test_load_asset_manifest_static_root_invalid_json(static_root):
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "manifest.json"
    manifest_path.write_text("{ invalid json here }")

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest is None


def test_load_asset_manifest_static_root_permission_error(static_root, monkeypatch):
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    manifest_path = django_bird_dir / "manifest.json"
    manifest_path.write_text("{}")

    # Mock open to raise permission error for this specific path
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise PermissionError("Permission denied")
        return open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_with_error)

    loaded_manifest = load_asset_manifest()
    assert loaded_manifest is None


def test_generate_asset_manifest(templates_dir, registry):
    template1 = templates_dir / "test_manifest1.html"
    template1.write_text("""
    <html>
    <head>
        <title>Test</title>
    </head>
    <body>
        {% bird button %}Button{% endbird %}
        {% bird card %}Card{% endbird %}
    </body>
    </html>
    """)

    template2 = templates_dir / "test_manifest2.html"
    template2.write_text("""
    <html>
    <head>
        <title>Test</title>
    </head>
    <body>
        {% bird accordion %}Accordion{% endbird %}
        {% bird tab %}Tab{% endbird %}
    </body>
    </html>
    """)

    TestComponent(name="button", content="<button>{{ slot }}</button>").create(
        templates_dir
    )
    TestComponent(name="card", content="<div class='card'>{{ slot }}</div>").create(
        templates_dir
    )
    TestComponent(
        name="accordion", content="<div class='accordion'>{{ slot }}</div>"
    ).create(templates_dir)
    TestComponent(name="tab", content="<div class='tab'>{{ slot }}</div>").create(
        templates_dir
    )

    manifest = generate_asset_manifest()

    all_keys = list(manifest.keys())
    template1_key = [k for k in all_keys if str(template1) in k][0]
    template2_key = [k for k in all_keys if str(template2) in k][0]

    assert sorted(manifest[template1_key]) == sorted(["button", "card"])
    assert sorted(manifest[template2_key]) == sorted(["accordion", "tab"])


def test_save_and_load_asset_manifest(tmp_path):
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    output_path = tmp_path / "test-manifest.json"

    save_asset_manifest(test_manifest_data, output_path)

    assert output_path.exists()

    with open(output_path) as f:
        loaded_data = json.load(f)

    assert loaded_data == test_manifest_data


def test_default_manifest_path():
    with override_settings(STATIC_ROOT="/path/to/static"):
        path = default_manifest_path()
        assert path == Path("/path/to/static/django_bird/manifest.json")

    with override_settings(STATIC_ROOT=None):
        path = default_manifest_path()
        assert path == Path("django_bird-asset-manifest.json")


class TestManagementCommand:
    """Tests for the generate_asset_manifest management command."""

    def test_generate_asset_manifest_command_default(self, static_root, templates_dir):
        TestComponent(name="test_cmd", content="<div>{{ slot }}</div>").create(
            templates_dir
        )

        template_path = templates_dir / "manifest_cmd_test.html"
        template_path.write_text("""
        <html>
        <body>
            {% bird test_cmd %}Test Command{% endbird %}
        </body>
        </html>
        """)

        stdout = StringIO()

        call_command("generate_asset_manifest", stdout=stdout)

        output = stdout.getvalue()

        assert "Asset manifest generated successfully" in output

        manifest_path = static_root / "django_bird" / "manifest.json"
        assert manifest_path.exists()

        with open(manifest_path) as f:
            manifest_data = json.load(f)

        template_keys = [
            k for k in manifest_data.keys() if "manifest_cmd_test.html" in k
        ]
        assert len(template_keys) == 1
        assert "test_cmd" in manifest_data[template_keys[0]]

    def test_generate_asset_manifest_command_with_options(
        self, tmp_path, templates_dir
    ):
        TestComponent(name="test_cmd2", content="<div>{{ slot }}</div>").create(
            templates_dir
        )

        template_path = templates_dir / "manifest_cmd_options.html"
        template_path.write_text("""
        <html>
        <body>
            {% bird test_cmd2 %}Test Command 2{% endbird %}
        </body>
        </html>
        """)

        custom_output = tmp_path / "custom" / "manifest.json"

        stdout = StringIO()

        call_command(
            "generate_asset_manifest",
            output=str(custom_output),
            stdout=stdout,
        )

        output = stdout.getvalue()

        assert f"Asset manifest generated successfully at {custom_output}" in output
        assert custom_output.exists()

        with open(custom_output) as f:
            content = f.read()
            manifest_data = json.loads(content)

        template_keys = [
            k for k in manifest_data.keys() if "manifest_cmd_options.html" in k
        ]

        assert len(template_keys) == 1
        assert "test_cmd2" in manifest_data[template_keys[0]]
