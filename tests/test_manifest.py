from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings

from django_bird.manifest import default_manifest_path
from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import load_asset_manifest
from django_bird.manifest import save_asset_manifest


@pytest.fixture(autouse=True)
def reset_manifest_cache():
    """Reset the manifest cache before and after each test."""
    # Access and reset the private module-level cache variable
    import django_bird.manifest

    django_bird.manifest._manifest_cache = None
    yield
    django_bird.manifest._manifest_cache = None


def test_load_asset_manifest_with_asset_manifest_setting(tmp_path):
    """Test loading manifest from a file specified in ASSET_MANIFEST setting."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create manifest file
    manifest_path = tmp_path / "test-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(test_manifest_data, f)

    # Test loading with ASSET_MANIFEST setting
    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(manifest_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_load_asset_manifest_nonexistent():
    """Test loading manifest from a nonexistent file."""
    with override_settings(
        DJANGO_BIRD={"ASSET_MANIFEST": "/nonexistent/path/manifest.json"}
    ):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_invalid_json(tmp_path):
    """Test handling of invalid JSON in manifest file."""
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{ this is not valid JSON }")

    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(invalid_json_file)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_permission_error(tmp_path, monkeypatch):
    """Test handling of permission errors when loading the manifest."""
    manifest_path = tmp_path / "permission-error.json"
    manifest_path.write_text("{}")

    # Mock open to raise a permission error
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise PermissionError("Permission denied")
        return open(*args, **kwargs)

    # Apply the mock
    monkeypatch.setattr("builtins.open", mock_open_with_error)

    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(manifest_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_os_error(tmp_path, monkeypatch):
    """Test handling of OS errors when loading the manifest."""
    manifest_path = tmp_path / "os-error.json"
    manifest_path.write_text("{}")

    # Mock open to raise an OS error
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise OSError("I/O error")
        return open(*args, **kwargs)

    # Apply the mock
    monkeypatch.setattr("builtins.open", mock_open_with_error)

    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(manifest_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_from_static_root(tmp_path):
    """Test loading manifest from the default STATIC_ROOT path."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create STATIC_ROOT structure
    static_root = tmp_path / "static"
    static_root.mkdir()
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    # Create manifest file in default location
    manifest_path = django_bird_dir / "asset-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(test_manifest_data, f)

    # Test loading with STATIC_ROOT setting but no ASSET_MANIFEST
    with override_settings(STATIC_ROOT=str(static_root), DJANGO_BIRD={}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_load_asset_manifest_static_root_invalid_json(tmp_path):
    """Test handling invalid JSON in STATIC_ROOT manifest."""
    # Create STATIC_ROOT structure
    static_root = tmp_path / "static-invalid"
    static_root.mkdir()
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    # Create invalid JSON manifest
    manifest_path = django_bird_dir / "asset-manifest.json"
    manifest_path.write_text("{ invalid json here }")

    # Test loading with invalid JSON
    with override_settings(STATIC_ROOT=str(static_root), DJANGO_BIRD={}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_static_root_permission_error(tmp_path, monkeypatch):
    """Test handling permission errors with STATIC_ROOT manifest."""
    # Create STATIC_ROOT structure
    static_root = tmp_path / "static-perm-error"
    static_root.mkdir()
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    # Create manifest file
    manifest_path = django_bird_dir / "asset-manifest.json"
    manifest_path.write_text("{}")

    # Mock open to raise permission error for this specific path
    def mock_open_with_error(*args, **kwargs):
        if str(manifest_path) in str(args[0]):
            raise PermissionError("Permission denied")
        return open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_with_error)

    # Test loading with permission error
    with override_settings(STATIC_ROOT=str(static_root), DJANGO_BIRD={}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_generate_asset_manifest(tmp_path, templates_dir, registry):
    """Test generating a manifest from a real template scan."""
    # Create test templates with components
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

    # Create the components
    from tests.utils import TestComponent

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

    # Use the registry fixture to discover components
    registry.discover_components()

    # Generate the manifest
    manifest = generate_asset_manifest()

    # Check that our test templates are in the manifest
    # We don't know the exact paths, so we need to check differently
    all_keys = list(manifest.keys())
    template1_key = [k for k in all_keys if str(template1) in k][0]
    template2_key = [k for k in all_keys if str(template2) in k][0]

    # Verify component names in template1
    assert sorted(manifest[template1_key]) == sorted(["button", "card"])

    # Verify component names in template2
    assert sorted(manifest[template2_key]) == sorted(["accordion", "tab"])


def test_save_and_load_asset_manifest(tmp_path):
    """Test saving and loading a manifest."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create output path
    output_path = tmp_path / "test-manifest.json"

    # Save manifest
    save_asset_manifest(test_manifest_data, output_path)

    # Verify file exists
    assert output_path.exists()

    # Load and verify contents directly
    with open(output_path) as f:
        loaded_data = json.load(f)

    assert loaded_data == test_manifest_data

    # Also verify using the load_asset_manifest function
    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(output_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_default_manifest_path():
    """Test the default_manifest_path function."""

    # Test with STATIC_ROOT
    with override_settings(STATIC_ROOT="/path/to/static"):
        path = default_manifest_path()
        assert path == Path("/path/to/static/django_bird/asset-manifest.json")

    # Test without STATIC_ROOT
    with override_settings(STATIC_ROOT=None):
        path = default_manifest_path()
        assert path == Path("django_bird-asset-manifest.json")


class TestManagementCommand:
    """Tests for the generate_asset_manifest management command."""

    def test_generate_asset_manifest_command_default(
        self, tmp_path, templates_dir, registry
    ):
        """Test running the command with default options."""
        # Create a test component
        from tests.utils import TestComponent

        TestComponent(name="test_cmd", content="<div>{{ slot }}</div>").create(
            templates_dir
        )

        # Create a template that uses the component
        template_path = templates_dir / "manifest_cmd_test.html"
        template_path.write_text("""
        <html>
        <body>
            {% bird test_cmd %}Test Command{% endbird %}
        </body>
        </html>
        """)

        # Discover components
        registry.discover_components()

        # Set up STATIC_ROOT for the test
        static_root = tmp_path / "static_root"
        static_root.mkdir()

        # Capture command output
        stdout = StringIO()

        # Run the command
        with override_settings(STATIC_ROOT=str(static_root)):
            call_command("generate_asset_manifest", stdout=stdout)

        # Check output message
        output = stdout.getvalue()
        assert "Asset manifest generated successfully" in output

        # Check that the manifest file was created
        manifest_path = static_root / "django_bird" / "asset-manifest.json"
        assert manifest_path.exists()

        # Check manifest content
        with open(manifest_path) as f:
            manifest_data = json.load(f)

        # Find the test template in the manifest
        template_keys = [
            k for k in manifest_data.keys() if "manifest_cmd_test.html" in k
        ]
        assert len(template_keys) == 1
        assert "test_cmd" in manifest_data[template_keys[0]]

    def test_generate_asset_manifest_command_with_options(
        self, tmp_path, templates_dir, registry
    ):
        """Test running the command with custom output path and pretty option."""
        # Create a test component
        from tests.utils import TestComponent

        TestComponent(name="test_cmd2", content="<div>{{ slot }}</div>").create(
            templates_dir
        )

        # Create a template that uses the component
        template_path = templates_dir / "manifest_cmd_options.html"
        template_path.write_text("""
        <html>
        <body>
            {% bird test_cmd2 %}Test Command 2{% endbird %}
        </body>
        </html>
        """)

        # Discover components
        registry.discover_components()

        # Define custom output path
        custom_output = tmp_path / "custom" / "asset-manifest.json"

        # Capture command output
        stdout = StringIO()

        # Run the command with custom options
        call_command(
            "generate_asset_manifest",
            output=str(custom_output),
            pretty=True,
            stdout=stdout,
        )

        # Check output message
        output = stdout.getvalue()
        assert f"Asset manifest generated successfully at {custom_output}" in output

        # Check that the manifest file was created
        assert custom_output.exists()

        # Check manifest content
        with open(custom_output) as f:
            content = f.read()
            manifest_data = json.loads(content)

        # Verify it's pretty-printed (has newlines)
        assert "\n" in content

        # Find the test template in the manifest
        template_keys = [
            k for k in manifest_data.keys() if "manifest_cmd_options.html" in k
        ]
        assert len(template_keys) == 1
        assert "test_cmd2" in manifest_data[template_keys[0]]
