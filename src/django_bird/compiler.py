from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum
from typing import Any


class CompilerError(Exception):
    """Base class for compiler errors."""


class LexerError(CompilerError):
    """Raised when an error occurs during lexical analysis."""


class ParserError(CompilerError):
    """Raised when an error occurs during parsing."""


class RendererError(CompilerError):
    """Raised when an error occurs during code generation."""


BIRD_PATTERN = re.compile(
    r"<bird:(\w+)([^>]*)(?:/>|>(.*?)</bird:\1>)", re.DOTALL | re.MULTILINE
)
SCRIPT_PATTERN = re.compile(r"<script>(.*?)</script>", re.DOTALL)
STYLE_PATTERN = re.compile(r"<style>(.*?)</style>", re.DOTALL)


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


@dataclass(frozen=True)
class ScriptNode:
    content: str


@dataclass(frozen=True)
class StyleNode:
    content: str


@dataclass(frozen=True)
class ElementNode:
    tag: str
    attributes: frozenset[
        tuple[str, str | int | bool | tuple[str, ...] | frozenset[tuple[str, str]]]
    ] = field(default_factory=frozenset)
    children: tuple[ElementNode | str | ComponentAST, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class TemplateNode:
    root: ElementNode | str | tuple[ElementNode | str, ...]


@dataclass(frozen=True)
class ComponentAST:
    scripts: tuple[ScriptNode, ...] = field(default_factory=tuple)
    styles: tuple[StyleNode, ...] = field(default_factory=tuple)
    template: TemplateNode = field(default_factory=lambda: TemplateNode(()))


class Parser:
    def __init__(self):
        self.template = ""
        self.pos = 0

    def reset(self):
        self.__init__()

    def parse(self, tokens: list[tuple[Token, str]]) -> ComponentAST:
        self.reset()  # Ensure we start with a clean state
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

        root_elements = self.parse_template(template_content)

        if len(root_elements) == 1:
            template = TemplateNode(root_elements[0])
        else:
            template = TemplateNode(tuple(root_elements))

        return ComponentAST(tuple(scripts), tuple(styles), template)

    def parse_template(self, template_content: str) -> list[ElementNode | str]:
        self.reset(template=template_content, pos=0)
        return self._parse_elements()

    def _parse_elements(self) -> list[ElementNode | str]:
        elements = []
        while self.pos < len(self.template):
            self._skip_whitespace()
            if self.template.startswith("</", self.pos):
                # Check for any closing tag
                if re.match(r"</[^\s>]+", self.template[self.pos :]):
                    break
            elif self.template.startswith("<!--", self.pos):
                self._skip_comment()
            elif self.template.startswith("<", self.pos):
                elements.append(self._parse_element())
            else:
                text = self._parse_text()
                if text.strip():
                    elements.append(text)
        return elements

    def _parse_element(self) -> ElementNode:
        self._expect("<")
        tag = self._parse_tag()
        attributes = self._parse_attributes()

        if self.template.startswith("/>", self.pos):
            self.pos += 2
            return ElementNode(tag, attributes)

        self._expect(">")
        children = self._parse_elements()
        self._expect(f"</{tag}>")

        return ElementNode(tag, attributes, tuple(children))

    def _parse_tag(self) -> str:
        match = re.match(r"[^\s>]+", self.template[self.pos :])
        if not match:
            raise ParserError(f"Expected tag name at position {self.pos}")
        self.pos += match.end()
        return match.group()

    def _parse_attributes(
        self,
    ) -> frozenset[
        tuple[str, str | int | bool | tuple[str, ...] | frozenset[tuple[str, str]]]
    ]:
        attributes = set()
        while True:
            self._skip_whitespace()
            if self.template.startswith(">", self.pos) or self.template.startswith(
                "/>", self.pos
            ):
                break

            key = self._parse_attribute_key()
            value = self._parse_attribute_value()

            if value is None:
                attributes.add((key, True))  # Boolean attribute
            elif value.isdigit():
                attributes.add((key, int(value)))
            elif value.lower() in ("true", "false"):
                attributes.add((key, value.lower() == "true"))
            else:
                attributes.add((key, value))

        return frozenset(attributes)

    def _parse_attribute_key(self) -> str:
        match = re.match(r"[^\s=/>]+", self.template[self.pos :])
        if not match:
            raise ParserError(f"Expected attribute name at position {self.pos}")
        self.pos += match.end()
        return match.group()

    def _parse_attribute_value(self) -> str | None:
        self._skip_whitespace()
        if self.template.startswith("=", self.pos):
            self.pos += 1
            self._skip_whitespace()
            quote = self.template[self.pos]
            if quote not in ('"', "'"):
                raise ParserError(
                    f"Expected quote for attribute value at position {self.pos}"
                )
            self.pos += 1
            try:
                end = self.template.index(quote, self.pos)
            except ValueError as e:
                raise ParserError(
                    f"Unclosed attribute value starting at position {self.pos}"
                ) from e
            value = self.template[self.pos : end]
            self.pos = end + 1
            return value
        return None

    def _parse_text(self) -> str:
        start = self.pos
        while self.pos < len(self.template) and self.template[self.pos] != "<":
            self.pos += 1
        return self.template[start : self.pos]

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.template) and self.template[self.pos].isspace():
            self.pos += 1

    def _skip_comment(self) -> None:
        end = self.template.index("-->", self.pos)
        self.pos = end + 3

    def _expect(self, expected: str) -> None:
        if not self.template.startswith(expected, self.pos):
            raise ParserError(f"Expected '{expected}' at position {self.pos}")
        self.pos += len(expected)


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
        return hashlib.sha256(content.encode()).hexdigest()[:8]

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
        return re.sub(
            r"([^\r\n,{}]+)(,(?=[^}]*{)|\s*{)",
            f'[data-bird-component-id="{component_id}"] \\1\\2',
            style_content,
        )

    def _render_template(
        self,
        template: TemplateNode,
        component_id: str | None = None,
        include_component_id: bool = True,
    ) -> str:
        def render_element(element: ElementNode | str) -> str:
            if isinstance(element, str):
                return element

            attributes = self._render_attributes(
                element.attributes, component_id if include_component_id else None
            )

            if not element.children:
                return f"<{element.tag} {attributes} />"

            children = "".join(render_element(child) for child in element.children)
            return f"<{element.tag} {attributes}>{children}</{element.tag}>"

        if isinstance(template.root, (ElementNode, str)):
            return render_element(template.root)
        else:
            return "".join(render_element(elem) for elem in template.root)

    def _render_attributes(
        self,
        attributes: frozenset[
            tuple[str, str | int | bool | tuple[str, ...] | frozenset[tuple[str, str]]]
        ],
        component_id: str | None = None,
    ) -> str:
        attr_strings = []
        if component_id:
            attr_strings.append(f'data-bird-component-id="{component_id}"')

        def format_value(v):
            if isinstance(v, (str, int)):
                return str(v)
            elif isinstance(v, bool):
                return str(v).lower()
            elif isinstance(v, tuple):
                return " ".join(map(str, v))
            elif isinstance(v, frozenset):
                return " ".join(f"{k}:{v}" for k, v in sorted(v))
            else:
                return str(v)

        for key, value in dict(attributes).items():
            if isinstance(value, bool):
                if value:
                    attr_strings.append(value)
            else:
                attr_strings.append(f'{key}="{format_value(value)}"')

        return " ".join(attr_strings)


class Compiler:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.renderer = Renderer()

    def compile(self, input_string: str) -> dict[str, Any]:
        try:
            tokens = self.lexer.tokenize(input_string)
            ast = self.parser.parse(tokens)
            return self.renderer.render(ast)
        except CompilerError as e:
            print(f"Compilation error: {str(e)}")
            raise e
