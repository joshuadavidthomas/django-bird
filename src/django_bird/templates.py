from __future__ import annotations

from .conf import app_settings


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
    template_names = []
    component_dirs = list(dict.fromkeys([*app_settings.COMPONENT_DIRS, "bird"]))

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

    return list(dict.fromkeys(template_names))
