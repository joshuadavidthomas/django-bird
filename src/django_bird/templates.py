from __future__ import annotations

import logging
import multiprocessing
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterator
from itertools import chain
from multiprocessing import Pool
from pathlib import Path
from typing import Any
from typing import TypeGuard
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

from django_bird import hookimpl

from .conf import app_settings
from .templatetags.tags.bird import BirdNode
from .utils import get_files_from_dirs
from .utils import unique_ordered

logger = logging.getLogger(__name__)


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


@hookimpl(specname="get_template_directories")
def get_default_engine_directories() -> list[Path]:
    engine = Engine.get_default()
    return [Path(dir) for dir in engine.dirs]


@hookimpl(specname="get_template_directories")
def get_app_template_directories() -> list[Path]:
    return [Path(dir) for dir in get_app_template_dirs("templates")]


def get_template_directories() -> Generator[Path, Any, None]:
    from django_bird.plugins import pm

    for hook_result in pm.hook.get_template_directories():
        yield from hook_result


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


def gather_bird_tag_template_usage() -> Generator[tuple[Path, set[str]], Any, None]:
    template_dirs = get_template_directories()
    templates = list(get_files_from_dirs(template_dirs))
    chunk_size = max(1, len(templates) // multiprocessing.cpu_count() * 2)
    chunks = [
        templates[i : i + chunk_size] for i in range(0, len(templates), chunk_size)
    ]
    with Pool() as pool:
        results = pool.map(_process_template_chunk, chunks)
    yield from chain.from_iterable(results)


def _process_template_chunk(  # pragma: no cover
    templates: list[tuple[Path, Path]],
) -> list[tuple[Path, set[str]]]:
    results: list[tuple[Path, set[str]]] = []
    for path, root in templates:
        template_name = str(path.relative_to(root))
        components = find_components_in_template(template_name)
        if components:
            results.append((path, components))
    return results


def find_components_in_template(template_path: str | Path) -> set[str]:
    """Find all component names used in a specific template.

    Args:
        template_path: Path to the template file or template name

    Returns:
        set[str]: Set of component names used in the template
    """
    template_name = str(template_path)

    visitor = NodeVisitor(Engine.get_default())
    try:
        template = Engine.get_default().get_template(template_name)
        context = Context()
        with context.bind_template(template):
            visitor.visit(template, context)
        return visitor.components
    except (TemplateDoesNotExist, TemplateSyntaxError, UnicodeDecodeError) as e:
        # If we can't load or process the template for any reason, log the exception and return an empty set
        logger.debug(
            f"Could not process template {template_name!r}: {e.__class__.__name__}: {e}"
        )
        return set()


NodeVisitorMethod = Callable[[Template | Node, Context], None]


def has_nodelist(node: Template | Node) -> TypeGuard[Template]:
    return hasattr(node, "nodelist")


@final
class NodeVisitor:  # pragma: no cover
    def __init__(self, engine: Engine):
        self.engine = engine
        self.components: set[str] = set()
        self.visited_templates: set[str] = set()

    def visit(self, node: Template | Node, context: Context) -> None:
        method_name = f"visit_{node.__class__.__name__}"
        visitor: NodeVisitorMethod = getattr(self, method_name, self.generic_visit)
        return visitor(node, context)

    def generic_visit(self, node: Template | Node, context: Context) -> None:
        if not has_nodelist(node) or node.nodelist is None:
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
            if not isinstance(included_templates, list | tuple):
                included_templates = [included_templates]
            for template_name in included_templates:
                included_template = self.engine.get_template(template_name)
                self.visit(included_template, context)
        except Exception as e:
            logger.debug(
                f"Error processing included template in NodeVisitor: {e.__class__.__name__}: {e}"
            )
        self.generic_visit(node, context)
