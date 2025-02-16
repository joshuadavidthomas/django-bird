# Plugins

django-bird uses a plugin system based on [pluggy](https://pluggy.readthedocs.io/) to allow extending its functionality.

## Available Hooks

<!-- [[[cog
from django.conf import settings

settings.configure(INSTALLED_APPS=["django_bird"])

import cog
import inspect
from django_bird.plugins import hookspecs
from typing import get_type_hints

hook_functions = [
    obj for name, obj in inspect.getmembers(hookspecs)
    if inspect.isfunction(obj) and obj.__module__ == 'django_bird.plugins.hookspecs'
]

for func in hook_functions:
    hints = get_type_hints(func)

    params = []
    for name, hint in hints.items():
        if name != 'return':
            params.append(f"{name}: {hint.__module__}.{hint.__name__}")

    return_type = hints['return']

    full_sig = f"{func.__name__}({', '.join(params)}) -> {return_type}"

    cog.outl(f"````{{py:function}} {full_sig}")
    cog.outl(f":canonical: django_bird.plugins.hookspecs.{func.__name__}\n")

    if func.__doc__:
        cog.outl(f"```{{autodoc2-docstring}} django_bird.plugins.hookspecs.{func.__name__}")
        cog.outl(":parser: myst")
        cog.outl("```")

    cog.outl("````\n")
# ]]] -->
````{py:function} collect_component_assets(template_path: pathlib.Path) -> collections.abc.Iterable[django_bird.staticfiles.Asset]
:canonical: django_bird.plugins.hookspecs.collect_component_assets

```{autodoc2-docstring} django_bird.plugins.hookspecs.collect_component_assets
:parser: myst
```
````

<!-- [[[end]]] -->

## Creating a Plugin

To create a plugin:

1. Create a Python package for your plugin
2. Import the `django_bird.hookimpl` marker:

   ```python
   from django_bird import hookimpl
   ```

3. Implement one or more hooks using the `@hookimpl` decorator.
4. Register your plugin in your package's entry points:

   ```toml
   [project.entry-points."django_bird"]
   my_plugin = "my_plugin.module"
   ```

See the [pluggy documentation](https://pluggy.readthedocs.io/) for more details.
