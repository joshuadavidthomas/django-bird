# Plugins

django-bird uses a plugin system based on [pluggy](https://pluggy.readthedocs.io/) to allow extending its functionality.

## Available Hooks

````{py:function} collect_component_assets(template_path: pathlib.Path) -> collections.abc.Iterable[django_bird.staticfiles.Asset]
:canonical: django_bird.plugins.hookspecs.collect_component_assets

```{autodoc2-docstring} django_bird.plugins.hookspecs.collect_component_assets
:parser: myst
```
````

````{py:function} get_template_directories() -> list[pathlib.Path]
:canonical: django_bird.plugins.hookspecs.get_template_directories

```{autodoc2-docstring} django_bird.plugins.hookspecs.get_template_directories
:parser: myst
```
````

````{py:function} pre_ready() -> None
:canonical: django_bird.plugins.hookspecs.pre_ready

```{autodoc2-docstring} django_bird.plugins.hookspecs.pre_ready
:parser: myst
```
````

````{py:function} ready() -> None
:canonical: django_bird.plugins.hookspecs.ready

```{autodoc2-docstring} django_bird.plugins.hookspecs.ready
:parser: myst
```
````

````{py:function} register_asset_types(register_type: collections.abc.Callable[[django_bird.staticfiles.AssetType], None]) -> None
:canonical: django_bird.plugins.hookspecs.register_asset_types

```{autodoc2-docstring} django_bird.plugins.hookspecs.register_asset_types
:parser: myst
```
````

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
