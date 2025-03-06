# Configuration

## Django settings

To use django-bird, you need to configure a few settings in your project:

1. Add django-bird's static file finder to your STATICFILES_FINDERS.
2. Add django-bird's template tags to Django's built-ins. **Note**: This is not required, but if you do not do this you will need to use `{% load django_bird %}` in any templates using components.

```{admonition} Auto Configuration
:class: tip

For automatic configuration of these settings, you can use the [django-bird-autoconf](https://pypi.org/project/django-bird-autoconf/) plugin. This plugin will handle all the setup for you automatically.
```

The complete setup in your settings file should look like this:

```{code-block} python
:caption: settings.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "OPTIONS": {
            "builtins": [
                "django_bird.templatetags.django_bird",
            ],
        },
    }
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_bird.staticfiles.BirdAssetFinder",
]
```

This configuration ensures that django-bird's templatetags are available globally and component assets can be properly discovered.
Configuration of django-bird is done through a `DJANGO_BIRD` dictionary in your Django settings.

## Application settings

All app settings are optional. Here is an example configuration with the types and default values shown:

```{code-block} python
:caption: settings.py

from pathlib import Path

DJANGO_BIRD = {
    "COMPONENT_DIRS": list[Path | str] = [],
    "ENABLE_BIRD_ATTRS": bool = True,
    "ADD_ASSET_PREFIX": bool | None = None,
}
```

### `COMPONENT_DIRS`

Additional directories to scan for components. Takes a list of paths relative to the base directory of your project's templates directory. A path can either be a `str` or `Path`.

By default, django-bird will look for components in a `bird` directory. Any directories specified here will take precedence and take priority when performing template resolution for components.

#### Example

Suppose you want to store your components in a `components` directory, you're using a third-party library that provides its own bird components, and you have an alternate templates directory.

You can configure django-bird to look in all these locations:

```{code-block} python
:caption: settings.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent

DJANGO_BIRD = {
    "COMPONENT_DIRS": [
        "components",
        Path("third_party_library/components"),
        BASE_DIR / "alternate_templates" / "bird",
    ]
}
```

In this configuration:

- `"components"` is a string path relative to your project's templates directory.
- `Path("third_party_library/components")` uses the `Path` object for the third-party library's components.
- `BASE_DIR / "alternate_templates" / "bird"` constructs a path using Django's `BASE_DIR` setting, similar to how other Django settings can be configured.

With this setup, django-bird will search for components in the following order:

1. `components`
2. `third_party_library/components`
3. `alternate_templates/bird`
4. The default `bird` directory

The default `bird` directory will always be checked last, ensuring that your custom directories take precedence in template resolution.


### `ENABLE_BIRD_ATTRS`

Controls whether components automatically receive data attributes related to django-bird in its `attrs` template context variable. Defaults to `True`.

See [Component ID Attribute](params.md#component-id-attribute) for more details on how this works.

### `ADD_ASSET_PREFIX`

Controls whether the app label prefix (`django_bird/`) is added to component asset URLs. This setting has three possible values:

- `None` (default): Automatically add the prefix in production (when `DEBUG = False`) but not in development mode. This matches Django's standard behavior where staticfiles are served directly from source directories in development but collected into a central location in production.

- `True`: Always add the prefix, regardless of the `DEBUG` setting. This is useful if you want consistent URL paths in all environments.

- `False`: Never add the prefix, regardless of the `DEBUG` setting. This is useful for custom static file configurations or when you're manually managing the directory structure.

#### Example Use Cases

- **Testing Environment**: In test environments, especially with Playwright or Selenium e2e tests, you may want to set:

  ```python
  DJANGO_BIRD = {"ADD_ASSET_PREFIX": False}
  ```

  This ensures your tests can find static assets without the prefix, even when `DEBUG = False`.

- **Custom Static File Handling**: If you have a custom static file setup that doesn't follow Django's conventions, you can configure the appropriate value based on your needs.
