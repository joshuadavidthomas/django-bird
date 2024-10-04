# django-bird

[![PyPI](https://img.shields.io/pypi/v/bird)](https://pypi.org/project/bird/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bird)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1-%2344B78B?labelColor=%23092E20)
<!-- https://shields.io/badges -->
<!-- django-4.2 | 5.0 | 5.1-#44B78B -->
<!-- labelColor=%23092E20 -->

High-flying components for perfectionists with deadlines.

> [!CAUTION]
> This is an experimental, pre-alpha attempt at a different approach to defining components in Django templates. It is not suitable for production use yet.

## Requirements

- Python 3.10, 3.11, 3.12, 3.13
- Django 4.2, 5.0, 5.1

## Installation

1. Install the package from PyPI:

```bash
python -m pip install django-bird
# or
uv add django-bird
uv sync
```

2. Add the app to your Django project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "django_bird",
    ...,
]
```

3. django-bird requires two settings in your `settings.TEMPLATES` to be configured to work properly:

    - `django_bird.templatetags.django_bird` in the `builtins`
    - `django_bird.loader.BirdLoader` in the innermost list of `loaders`, before `django.template.loaders.filesystem.Loader` and `django.template.loaders.app_directories.Loader`

    By default, these should be configured for you automatically. If you would like to disable this behavior, you will need to set `DJANGO_BIRD["ENABLE_AUTO_CONFIG"] = False`.

    ```python
    # settings.py
    DJANGO_BIRD = {
        "ENABLE_AUTO_CONFIG": False,
    }
    ```

## Getting Started

Coming soon...

## Documentation

Please refer to the [documentation](https://bird.readthedocs.io/) for more information.

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
