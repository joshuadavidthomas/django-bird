from __future__ import annotations

import re
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from typing import final

from django.template.base import Node
from django.template.base import Template
from django.template.context import Context
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError
from django.template.loader_tags import ExtendsNode
from django.template.loader_tags import IncludeNode
from django.template.utils import get_app_template_dirs

from django_bird.utils import unique_ordered

from ._typing import _has_nodelist
from .conf import app_settings
from .templatetags.tags.bird import TAG
from .templatetags.tags.bird import BirdNode
from .utils import get_files_from_dirs


def get_template_names(name: str) -> list[str]:
    """
    Generate a list of potential template names for a component.

    The function searches for templates in the following order (from most specific to most general):

    1. In a subdirectory named after the component, using the component name
    2. In the same subdirectory, using a fallback 'index.html'
    3. In parent directory for nested components
    4. In the base component directory, using the full component name

    The order of names is important as it determines the template resolution priority.
    This order allows for both direct matches and hierarchical component structures,
    with more specific paths taking precedence over more general ones.

    This order allows for:
    - Single file components
    - Multi-part components
    - Specific named files within component directories
    - Fallback default files for components

    For example:
    - For an "input" component, the ordering would be:
        1. `{component_dir}/input/input.html`
        2. `{component_dir}/input/index.html`
        3. `{component_dir}/input.html`
    - For an "input.label" component:
        1. `{component_dir}/input/label/label.html`
        2. `{component_dir}/input/label/index.html`
        3. `{component_dir}/input/label.html`
        4. `{component_dir}/input.label.html`

    Returns:
        list[str]: A list of potential template names in resolution order.
    """
    template_names: list[str] = []
    component_dirs = app_settings.get_component_directory_names()

    name_parts = name.split(".")
    path_name = "/".join(name_parts)

    for component_dir in component_dirs:
        potential_names = [
            f"{component_dir}/{path_name}/{name_parts[-1]}.html",
            f"{component_dir}/{path_name}/index.html",
            f"{component_dir}/{path_name}.html",
            f"{component_dir}/{name}.html",
        ]
        template_names.extend(potential_names)

    return unique_ordered(template_names)


def get_template_directories() -> Generator[Path, Any, None]:
    engine = Engine.get_default()
    for engine_dir in engine.dirs:
        yield Path(engine_dir)
    for app_dir in get_app_template_dirs("templates"):
        yield Path(app_dir)


def get_component_directories(
    template_dirs: Iterator[Path] | None = None,
) -> list[Path]:
    if template_dirs is None:
        template_dirs = get_template_directories()

    return [
        Path(template_dir) / component_dir
        for template_dir in template_dirs
        for component_dir in app_settings.get_component_directory_names()
    ]


BIRD_TAG_PATTERN = re.compile(rf"{{%\s*{TAG}\s+(.*?)\s*%}}", re.DOTALL)


def scan_file_for_bird_tag(path: Path) -> Generator[str, Any, None]:
    if not path.is_file():
        return

    with open(path) as f:
        for line in f:
            for match in BIRD_TAG_PATTERN.finditer(line):
                yield match.group(1).strip("'\"")


def gather_bird_tag_template_usage() -> Generator[tuple[Path, Path], Any, None]:
    template_dirs = get_template_directories()
    for path, root in get_files_from_dirs(template_dirs):
        bird_tag_usage = [line for line in scan_file_for_bird_tag(path)]
        if bird_tag_usage:
            yield path, root


def scan_template_for_bird_tag(template_name: str) -> set[str]:
    print(f"{template_name=}")
    engine = Engine.get_default()
    try:
        template = engine.get_template(template_name)
    except (TemplateDoesNotExist, TemplateSyntaxError):
        return set()
    context = Context()
    visitor = NodeVisitor(engine)
    with context.bind_template(template):
        visitor.visit(template, context)
    return visitor.components


NodeVisitorMethod = Callable[[Template | Node, Context], None]


@final
class NodeVisitor:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.components: set[str] = set()
        self.visited_templates: set[str] = set()

    def visit(self, node: Template | Node, context: Context) -> None:
        method_name = f"visit_{node.__class__.__name__}"
        visitor: NodeVisitorMethod = getattr(self, method_name, self.generic_visit)
        return visitor(node, context)

    def generic_visit(self, node: Template | Node, context: Context) -> None:
        if not _has_nodelist(node) or node.nodelist is None:
            return
        for child_node in node.nodelist:
            self.visit(child_node, context)

    def visit_Template(self, template: Template, context: Context) -> None:
        if template.name is None or template.name in self.visited_templates:
            return
        self.visited_templates.add(template.name)
        self.generic_visit(template, context)

    def visit_BirdNode(self, node: BirdNode, context: Context) -> None:
        component_name = node.name.strip("\"'")
        self.components.add(component_name)
        self.generic_visit(node, context)

    def visit_ExtendsNode(self, node: ExtendsNode, context: Context) -> None:
        parent_template = node.get_parent(context)
        self.visit(parent_template, context)
        self.generic_visit(node, context)

    def visit_IncludeNode(self, node: IncludeNode, context: Context) -> None:
        try:
            included_templates = node.template.resolve(context)
            if not isinstance(included_templates, (list, tuple)):
                included_templates = [included_templates]
            for template_name in included_templates:
                included_template = self.engine.get_template(template_name)
                self.visit(included_template, context)
        except Exception:
            pass
        self.generic_visit(node, context)
