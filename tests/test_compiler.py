from __future__ import annotations

from textwrap import dedent

import pytest

from django_bird.compiler import Compiler
from django_bird.compiler import ComponentAST
from django_bird.compiler import ElementNode
from django_bird.compiler import Lexer
from django_bird.compiler import LexerError
from django_bird.compiler import Parser
from django_bird.compiler import ParserError
from django_bird.compiler import Renderer
from django_bird.compiler import ScriptNode
from django_bird.compiler import StyleNode
from django_bird.compiler import TemplateNode
from django_bird.compiler import Token


def test_lexer_with_multiple_elements():
    template = "<style>body { background-color: red; }</style><h1>Welcome to my page {{ user.name }}</h1><script>console.log('Hello, world!');</script>"

    tokens = Lexer().tokenize(template)

    assert len(tokens) == 3
    assert tokens[0] == (Token.STYLE, "body { background-color: red; }")
    assert tokens[1] == (Token.TEMPLATE, "<h1>Welcome to my page {{ user.name }}</h1>")
    assert tokens[2] == (Token.SCRIPT, "console.log('Hello, world!');")


def test_lexer_with_unclosed_tags():
    lexer = Lexer()

    with pytest.raises(LexerError, match="Unclosed <style> tag"):
        lexer.tokenize("<style>body { color: red; }")
    with pytest.raises(LexerError, match="Unclosed <script> tag"):
        lexer.tokenize("<script>console.log('Hello');")


def test_lexer_with_empty_content():
    tokens = Lexer().tokenize("")

    assert len(tokens) == 0


def test_parser_with_nested_elements():
    template = '<div class="container"><h1>Title</h1><p>Paragraph <strong>with bold text</strong></p></div>'

    tokens = Lexer().tokenize(template)
    ast = Parser().parse(tokens)

    assert isinstance(ast, ComponentAST)
    assert len(ast.scripts) == 0
    assert len(ast.styles) == 0
    assert isinstance(ast.template.root, ElementNode)
    assert ast.template.root.tag == "div"
    assert ast.template.root.attributes == frozenset({"class": "container"}.items())
    assert len(ast.template.root.children) == 2


def test_parser_with_self_closing_tags():
    template = "<img src='image.jpg' alt='An image' />"

    tokens = Lexer().tokenize(template)
    ast = Parser().parse(tokens)

    assert isinstance(ast.template.root, ElementNode)
    assert ast.template.root.tag == "img"
    assert ast.template.root.attributes == frozenset(
        {"src": "image.jpg", "alt": "An image"}.items()
    )
    assert len(ast.template.root.children) == 0


def test_parser_with_custom_tags():
    template = "<bird:custom-element attr1='value1'>Content</bird:custom-element>"

    tokens = Lexer().tokenize(template)
    ast = Parser().parse(tokens)

    assert isinstance(ast.template.root, ElementNode)
    assert ast.template.root.tag == "bird:custom-element"
    assert ast.template.root.attributes == frozenset({"attr1": "value1"}.items())
    assert ast.template.root.children == ("Content",)


def test_renderer():
    ast = ComponentAST(
        scripts=(ScriptNode("console.log('Test');"),),
        styles=(StyleNode("body { color: blue; }"),),
        template=TemplateNode(
            ElementNode("div", frozenset({"class": "test"}.items()), ("Hello",))
        ),
    )

    result = Renderer().render(ast)

    assert "component_id" in result
    assert len(result["scripts"]) == 1
    assert "componentId" in result["scripts"][0]
    assert len(result["styles"]) == 1
    assert (
        f'[data-bird-component-id="{result["component_id"]}"] body'
        in result["styles"][0]
    )

    assert f'data-bird-component-id="{result["component_id"]}"' in result["template"]
    assert 'class="test"' in result["template"]
    assert result["template"].startswith("<div")
    assert "Hello" in result["template"]
    assert result["template"].endswith("</div>")


def test_compiler_end_to_end():
    template = "<style>body { background-color: red; }</style><h1>Welcome to my page {{ user.name }}</h1><script>console.log('Hello, world!');</script>"

    result = Compiler().compile(template)

    assert "component_id" in result
    assert len(result["scripts"]) == 1
    assert len(result["styles"]) == 1
    assert "body" in result["styles"][0]
    assert "Welcome to my page" in result["template"]


def test_compiler_with_empty_input():
    result = Compiler().compile("")

    assert result["component_id"]
    assert len(result["scripts"]) == 0
    assert len(result["styles"]) == 0
    assert result["template"] == ""


def test_compiler_with_only_text():
    template = "Just some text"

    result = Compiler().compile(template)

    assert result["template"] == "Just some text"


def test_compiler_with_malformed_html():
    compiler = Compiler()

    with pytest.raises(ParserError):
        compiler.compile("<div>Unclosed div")


def test_compiler_with_django_templatetags():
    template = dedent("""
    {% load static %}
    <div>
        <h1>{{ title }}</h1>
        <p>Welcome, {{ user.username }}</p>
        {% if is_staff %}
            <p>You have admin access.</p>
        {% endif %}
        <ul>
        {% for item in items %}
            <li>{{ item.name }} - ${{ item.price }}</li>
        {% endfor %}
        </ul>
    </div>
    """)

    result = Compiler().compile(template)

    assert "component_id" in result
    assert len(result["scripts"]) == 0
    assert len(result["styles"]) == 0
    assert "{{ title }}" in result["template"]
    assert "{{ user.username }}" in result["template"]
    assert "{% if is_staff %}" in result["template"]
    assert "{% for item in items %}" in result["template"]


def test_compiler_with_bird_component():
    template = dedent("""
    <bird:custom-button color="blue" size="large">
        Click me!
    </bird:custom-button>

    <script>
        document.querySelector('bird\\:custom-button').addEventListener('click', () => {
            console.log('Bird button clicked!');
        });
    </script>

    <style>
        bird\\:custom-button {
            padding: 10px 20px;
            border-radius: 5px;
        }
    </style>
    """)

    result = Compiler().compile(template)

    assert "component_id" in result
    assert len(result["scripts"]) == 1
    assert "Bird button clicked!" in result["scripts"][0]
    assert len(result["styles"]) == 1
    assert "bird\\:custom-button" in result["styles"][0]
    assert "<bird:custom-button" in result["template"]
    assert 'color="blue"' in result["template"]
    assert 'size="large"' in result["template"]
    assert "Click me!" in result["template"]
