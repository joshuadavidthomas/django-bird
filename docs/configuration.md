# Configuration

Configuration of django-bird is done through a `DJANGO_BIRD` dictionary in your Django settings.

All settings are optional. Here is an example configuration with the types and default values shown:

```{code-block} python
:caption: settings.py

from pathlib import Path

DJANGO_BIRD = {
    "COMPONENT_DIRS": list[Path | str] = [],
    "ENABLE_AUTO_CONFIG": bool = True,
    "ENABLE_BIRD_ATTRS": bool = True,
}
```

## `COMPONENT_DIRS`

Additional directories to scan for components. Takes a list of paths relative to the base directory of your project's templates directory. A path can either be a `str` or `Path`.

By default, django-bird will look for components in a `bird` directory. Any directories specified here will take precedence and take priority when performing template resolution for components.

### Example

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

## `ENABLE_AUTO_CONFIG`

django-bird requires a few settings to be setup in your project's `DJANGO_SETTINGS_MODULE` before it will work properly. django-bird will automatically take care of this, during the app's initialization in `django_bird.apps.AppConfig.ready`.

If you would like to disable this behavior and perform the setup manually, setting `ENABLE_AUTO_CONFIG` to `False` will allow you to do so.

### Manual Setup

When `ENABLE_AUTO_CONFIG` is set to `False`, you need to manually configure the following:

1. Add django-bird's template tags to Django's built-ins.

The complete setup in your settings file should look like this:

```{code-block} python
:caption: settings.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent

DJANGO_BIRD = {
    "ENABLE_AUTO_CONFIG": False,
}

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
```

This configuration ensures that django-bird's templatetags are available globally.

## `ENABLE_BIRD_ATTRS`

Controls whether components automatically receive data attributes related to django-bird in its `attrs` template context variable. Defaults to `True`.

See [Component ID Attribute](params.md#component-id-attribute) for more details on how this works.
