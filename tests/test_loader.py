from __future__ import annotations

import hashlib
from textwrap import dedent

import pytest
from django.conf import settings
from django.template.engine import Engine
from django.template.loader import get_template
from django.test import override_settings

from django_bird.compiler import BIRD_PATTERN
from django_bird.loader import BirdLoader


@pytest.fixture
def templates_dir(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return templates_dir


@pytest.fixture(autouse=True)
def override_templates_settings(templates_dir):
    with override_settings(
        TEMPLATES=[settings.TEMPLATES[0] | {"DIRS": [templates_dir]}]
    ):
        yield


@pytest.fixture
def bird_component(templates_dir):
    TEMPLATE = """\
<button>
    {% slot %}
    {% endslot %}
</button>\
"""
    bird_template_dir = templates_dir / "bird"
    bird_template_dir.mkdir()
    component = bird_template_dir / "button.html"
    component.write_text(TEMPLATE)
    return component


@pytest.fixture
def template_using_bird(templates_dir):
    TEMPLATE = """\
<bird:button>
    {{ text }}
</bird:button>\
"""
    template = templates_dir / "template.html"
    template.write_text(TEMPLATE)
    return template


@pytest.fixture
def nested_bird_component(templates_dir):
    BUTTON_TEMPLATE = """\
<button>
    {{ slot }}
    <bird:icon>icon</bird:icon>
</button>\
"""
    ICON_TEMPLATE = """\
{{ slot }}\
"""

    bird_template_dir = templates_dir / "bird"
    bird_template_dir.mkdir()
    button_component = bird_template_dir / "buttonicon.html"
    button_component.write_text(BUTTON_TEMPLATE)
    icon_component = bird_template_dir / "icon.html"
    icon_component.write_text(ICON_TEMPLATE)
    return button_component, icon_component


@pytest.fixture
def template_using_nested_bird(templates_dir):
    TEMPLATE = """\
<bird:buttonicon>
    {{ text }}
</bird:buttonicon>\
"""
    template = templates_dir / "template.html"
    template.write_text(TEMPLATE)
    return template


def test_render_template(bird_component, template_using_bird):
    context = {"text": "Button"}

    template = get_template(template_using_bird.name)
    rendered = template.render(context)

    assert "<bird:button" not in rendered


def test_render_template_nested(nested_bird_component, template_using_nested_bird):
    context = {"text": "Button"}

    template = get_template(template_using_nested_bird.name)
    rendered = template.render(context)

    assert "<bird:button" not in rendered


class TestBirdLoader:
    @pytest.fixture
    def loader(self):
        engine = Engine()
        return BirdLoader(engine)

    @pytest.mark.parametrize(
        "contents,expected",
        [
            (
                "<div>No bird here</div>",
                "<div>No bird here</div>",
            ),
            (
                "<bird:button class='btn'>Click me</bird:button>",
                "{% bird_component 'button' class='btn' %}Click me{% endbird_component %}",
            ),
            (
                "<bird:input type='text' name='username' required />",
                "{% bird_component 'input' type='text' name='username' required %}{% endbird_component %}",
            ),
            (
                dedent("""
                    <bird:card>
                        <bird:header>Title</bird:header>
                        <bird:body>Content</bird:body>
                    </bird:card>
                """),
                dedent("""
                    {% bird_component 'card' %}
                        {% bird_component 'header' %}Title{% endbird_component %}
                        {% bird_component 'body' %}Content{% endbird_component %}
                    {% endbird_component %}
                """),
            ),
            (
                "<bird:alert type='warning'><strong>Warning:</strong> This is important!</bird:alert>",
                "{% bird_component 'alert' type='warning' %}<strong>Warning:</strong> This is important!{% endbird_component %}",
            ),
            (
                dedent("""
                    <bird:list items='{{ items }}'>
                        {% for item in items %}
                            <li>{{ item }}</li>
                        {% endfor %}
                    </bird:list>
                """),
                dedent("""
                    {% bird_component 'list' items='{{ items }}' %}
                        {% for item in items %}
                            <li>{{ item }}</li>
                        {% endfor %}
                    {% endbird_component %}
                """),
            ),
            (
                "<bird:spacer />",
                "{% bird_component 'spacer' %}{% endbird_component %}",
            ),
            (
                "<bird:quote text=\"He said, 'Hello!'\" author='John Doe' />",
                "{% bird_component 'quote' text=\"He said, 'Hello!'\" author='John Doe' %}{% endbird_component %}",
            ),
            (
                dedent("""
                    <bird:header>Title</bird:header>
                    <p>Some text</p>
                    <bird:footer>Footer</bird:footer>
                """),
                dedent("""
                    {% bird_component 'header' %}Title{% endbird_component %}
                    <p>Some text</p>
                    {% bird_component 'footer' %}Footer{% endbird_component %}
                """),
            ),
        ],
    )
    def test_process_bird_components(self, contents, expected, loader):
        assert loader.process_bird_components(contents) == expected

    @pytest.mark.parametrize(
        "contents,expected",
        [
            (
                "<bird:button class='btn'>Click me</bird:button>",
                "{% bird_component 'button' class='btn' %}Click me{% endbird_component %}",
            ),
            (
                "<bird:spacer />",
                "{% bird_component 'spacer' %}{% endbird_component %}",
            ),
            (
                "<bird:input type='text' data-validate='true' placeholder='Enter name' required />",
                "{% bird_component 'input' type='text' data-validate='true' placeholder='Enter name' required %}{% endbird_component %}",
            ),
            (
                '<bird:modal title="Confirm Action" button-text=\'Say "Hello"\'>Are you sure?</bird:modal>',
                "{% bird_component 'modal' title=\"Confirm Action\" button-text='Say \"Hello\"' %}Are you sure?{% endbird_component %}",
            ),
            (
                dedent("""
                    <bird:card>
                        <h2>Title</h2>
                        <p>This is a
                            multiline content</p>
                    </bird:card>
                """),
                dedent("""
                    {% bird_component 'card' %}
                        <h2>Title</h2>
                        <p>This is a
                            multiline content</p>
                    {% endbird_component %}
                """),
            ),
        ],
    )
    def test_replace_bird(self, contents, expected, loader):
        match = BIRD_PATTERN.search(contents)

        assert loader.replace_bird(match) == expected.strip()

    def test_replace_bird_no_match(self, loader):
        with pytest.raises(ValueError):
            loader.replace_bird(None)

    def test_caching(self, loader):
        contents = "<bird:button>Click me</bird:button>"
        match = BIRD_PATTERN.search(contents)

        result1 = loader.replace_bird(match)

        cache_key = f"bird_template_{hashlib.sha256(contents.encode()).hexdigest()}"
        loader.cache.set(cache_key, "Cached result")

        result2 = loader.replace_bird(match)

        assert result2 == "Cached result"
        assert result1 != result2
