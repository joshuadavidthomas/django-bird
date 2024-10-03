from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum
from typing import Any

from bird_compiler import tokenize


class CompilerError(Exception):
    """Base class for compiler errors."""


class LexerError(CompilerError):
    """Raised when an error occurs during lexical analysis."""


class ParserError(CompilerError):
    """Raised when an error occurs during parsing."""


class RendererError(CompilerError):
    """Raised when an error occurs during code generation."""


ATTRIBUTE_PATTERN = re.compile(r'(\w+)(?:=["\'](.*?)["\'])?')
BIRD_PATTERN = re.compile(
    r"<bird:(\w+)([^>]*)(?:/>|>(.*?)</bird:\1>)", re.DOTALL | re.MULTILINE
)
SCRIPT_PATTERN = re.compile(r"<script>(.*?)</script>", re.DOTALL)
STYLE_PATTERN = re.compile(r"<style>(.*?)</style>", re.DOTALL)
TAG_PATTERN = re.compile(r"[^\s>]+")
STYLE_SCOPE_PATTERN = re.compile(r"([^\r\n,{}]+)(,(?=[^}]*{)|\s*{)")


class Token(IntEnum):
    SCRIPT = 1
    STYLE = 2
    TEMPLATE = 3


class Lexer:
    def tokenize(self, input_string: str) -> list[tuple[Token, str]]:
        tokens: list[tuple[Token, str]] = []
        remaining_content = input_string.strip()

        last_end = 0
        for token_type, match in sorted(
            self.find_matches(remaining_content), key=lambda x: x[1].start()
        ):
            start, end = match.span()

            if start > last_end:
                template_content = remaining_content[last_end:start].strip()
                if template_content:
                    tokens.append((Token.TEMPLATE, template_content))

            tokens.append((token_type, match.group(1).strip()))
            last_end = end

        if last_end < len(remaining_content):
            template_content = remaining_content[last_end:].strip()
            if template_content:
                tokens.append((Token.TEMPLATE, template_content))

        if "<style>" in input_string and "</style>" not in input_string:
            raise LexerError("Unclosed <style> tag")
        if "<script>" in input_string and "</script>" not in input_string:
            raise LexerError("Unclosed <script> tag")

        return tokens

    def find_matches(self, content: str):
        for pattern, token_type in [
            (SCRIPT_PATTERN, Token.SCRIPT),
            (STYLE_PATTERN, Token.STYLE),
        ]:
            for match in pattern.finditer(content):
                yield token_type, match


@dataclass(frozen=True, slots=True)
class ScriptNode:
    content: str


@dataclass(frozen=True, slots=True)
class StyleNode:
    content: str


@dataclass(frozen=True, slots=True)
class ElementNode:
    tag: str
    attributes: frozenset[
        tuple[str, str | int | bool | tuple[str, ...] | frozenset[tuple[str, str]]]
    ] = field(default_factory=frozenset)
    children: tuple[ElementNode | str | ComponentAST, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True, slots=True)
class TemplateNode:
    root: ElementNode | str | tuple[ElementNode | str, ...]


@dataclass(frozen=True, slots=True)
class ComponentAST:
    scripts: tuple[ScriptNode, ...] = field(default_factory=tuple)
    styles: tuple[StyleNode, ...] = field(default_factory=tuple)
    template: TemplateNode = field(default_factory=lambda: TemplateNode(()))


class Parser:
    def __init__(self):
        self.template = ""
        self.pos = 0
        self.ast: ComponentAST | None = None

    def reset(self, template: str = "", pos: int = 0):
        self.template = template
        self.pos = pos

    def parse(self, tokens: list[tuple[Token, str]]) -> ComponentAST:
        self.reset()
        scripts: list[ScriptNode] = []
        styles: list[StyleNode] = []
        template_content: str = ""

        for token_type, content in tokens:
            if token_type == Token.SCRIPT:
                scripts.append(ScriptNode(content))
            elif token_type == Token.STYLE:
                styles.append(StyleNode(content))
            elif token_type == Token.TEMPLATE:
                template_content += content

        self.reset(template=template_content)

        # Parse the root elements
        root_elements = self.parse_elements()

        if len(root_elements) == 1:
            template = TemplateNode(root_elements[0])
        else:
            template = TemplateNode(tuple(root_elements))

        self.ast = ComponentAST(tuple(scripts), tuple(styles), template)
        return self.ast

    def parse_elements(self) -> list[ElementNode | str]:
        elements = []
        end = len(self.template)
        while self.pos < end:
            char = self.template[self.pos]
            if char.isspace():
                self.pos += 1
            elif char == "<":
                if self.pos + 1 < end and self.template[self.pos + 1] == "/":
                    break
                elif (
                    self.pos + 3 < end
                    and self.template[self.pos : self.pos + 4] == "<!--"
                ):
                    end = self.template.index("-->", self.pos)
                    self.pos = end + 3
                else:
                    elements.append(self.parse_element())
            else:
                start = self.pos
                self.pos = self.template.find("<", start)
                if self.pos == -1:
                    self.pos = end
                text = self.template[start : self.pos].strip()
                if text:
                    elements.append(text)
        return elements

    def parse_element(self) -> ElementNode:
        if self.template[self.pos : self.pos + len("<")] != "<":
            raise ParserError(f"Expected '<' at position {self.pos}")
        self.pos += len("<")

        # find tag
        match = TAG_PATTERN.match(self.template[self.pos :])
        if not match:
            raise ParserError(f"Expected tag name at position {self.pos}")
        self.pos += match.end()
        tag = match.group()

        attributes = self.parse_attributes()

        # skip whitespace
        while self.pos < len(self.template) and self.template[self.pos].isspace():
            self.pos += 1
        char = self.template[self.pos]

        # Check for self-closing tag or opening tag
        if char == "/":
            self.pos += 2  # Skip "/>"
            return ElementNode(tag, attributes)
        elif char == ">":
            self.pos += 1
            children = self.parse_elements()
            if self.template[self.pos : self.pos + len(f"</{tag}>")] != f"</{tag}>":
                raise ParserError(f"Expected '</{tag}>' at position {self.pos}")
            self.pos += len(f"</{tag}>")
            return ElementNode(tag, attributes, tuple(children))
        else:
            raise ParserError(f"Unexpected character '{char}' at position {self.pos}")

    def parse_attributes(self) -> frozenset[tuple[str, Any]]:
        attributes = []
        end = len(self.template)
        while self.pos < end:
            # skip whitespace
            while self.pos < len(self.template) and self.template[self.pos].isspace():
                self.pos += 1
            if self.template[self.pos] in (">", "/"):
                break
            match = ATTRIBUTE_PATTERN.match(self.template, self.pos)
            if not match:
                break
            key, value = match.groups()
            self.pos = match.end()
            if value is None:
                attributes.append((key, True))
            elif value.isdigit():
                attributes.append((key, int(value)))
            elif value.lower() in ("true", "false"):
                attributes.append((key, value.lower() == "true"))
            else:
                attributes.append((key, value))
        return frozenset(attributes)


class Renderer:
    def render(self, ast: ComponentAST) -> dict[str, Any]:
        component_id = self._generate_component_id(ast)
        return {
            "component_id": component_id,
            "scripts": self._process_scripts(ast.scripts, component_id),
            "styles": self._process_styles(ast.styles, component_id),
            "template": self._render_template(ast.template, component_id),
        }

    def _generate_component_id(self, ast: ComponentAST) -> str:
        content = (
            "".join(script.content for script in ast.scripts)
            + "".join(style.content for style in ast.styles)
            + self._render_template(ast.template, include_component_id=False)
        )
        return hex(hash(content))[2:10]

    def _process_scripts(
        self, scripts: list[ScriptNode], component_id: str
    ) -> list[str]:
        return [self._wrap_script(script.content, component_id) for script in scripts]

    def _wrap_script(self, script_content: str, component_id: str) -> str:
        return f"""
(function() {{
    const componentId = "{component_id}";
    const componentElement = document.querySelector('[data-bird-component-id="{component_id}"]');
    {script_content}
}})();
"""

    def _process_styles(self, styles: list[StyleNode], component_id: str) -> list[str]:
        return [self._scope_style(style.content, component_id) for style in styles]

    def _scope_style(self, style_content: str, component_id: str) -> str:
        return STYLE_SCOPE_PATTERN.sub(
            f'[data-bird-component-id="{component_id}"] \\1\\2', style_content
        )

    def _render_template(
        self,
        template: TemplateNode,
        component_id: str | None = None,
        include_component_id: bool = True,
    ) -> str:
        def render_element(element: ElementNode | str | ComponentAST) -> list[str]:
            if isinstance(element, str):
                return [element]
            elif isinstance(element, ElementNode):
                parts = []
                attributes = self._render_attributes(
                    element.attributes, component_id if include_component_id else None
                )
                parts.append(f"<{element.tag} {attributes}")
                if not element.children:
                    parts.append("/>")
                else:
                    parts.append(">")
                    for child in element.children:
                        parts.extend(render_element(child))
                    parts.append(f"</{element.tag}>")
                return parts
            else:  # ComponentAST
                return [
                    self._render_template(
                        element.template, component_id, include_component_id
                    )
                ]

        if isinstance(template.root, (ElementNode, str, ComponentAST)):
            return "".join(render_element(template.root))
        else:
            parts = []
            for elem in template.root:
                parts.extend(render_element(elem))
            return "".join(parts)

    def _render_attributes(
        self,
        attributes: frozenset[tuple[str, Any]],
        component_id: str | None = None,
    ) -> str:
        attr_strings = (
            [f'data-bird-component-id="{component_id}"'] if component_id else []
        )
        attr_strings.extend(
            f'{key}="{value}"' if not isinstance(value, bool) else key
            for key, value in attributes
            if value is not False
        )
        return " ".join(attr_strings)


class Compiler:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.renderer = Renderer()

    def compile(self, input_string: str) -> dict[str, Any]:
        try:
            tokens = tokenize(input_string)
            # tokens = self.lexer.tokenize(input_string)
            ast = self.parser.parse(tokens)
            return self.renderer.render(ast)
        except CompilerError as e:
            print(f"Compilation error: {str(e)}")
            raise e
