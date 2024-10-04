<!-- docs-intro-begin -->
# django-bird

[![PyPI](https://img.shields.io/pypi/v/django-bird)](https://pypi.org/project/django-bird/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-bird)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1-%2344B78B?labelColor=%23092E20)
<!-- https://shields.io/badges -->
<!-- django-4.2 | 5.0 | 5.1-#44B78B -->
<!-- labelColor=%23092E20 -->

High-flying components for perfectionists with deadlines.

<!-- docs-intro-end -->
> [!CAUTION]
> This is an experimental, alpha attempt at a different approach to defining components in Django templates. It is not suitable for production use yet.

<!-- docs-content-begin -->
## Requirements

- Python 3.10, 3.11, 3.12, 3.13
- Django 4.2, 5.0, 5.1

## Installation

1. Install the package from PyPI:

    ```bash
    python -m pip install django-bird

    # or if you like the new hotness

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

3. django-bird will automatically configure the necessary settings in your project. No further action is required for most use cases.

    If you need to customize the configuration or prefer to set up django-bird manually, you can set `DJANGO_BIRD["ENABLE_AUTO_CONFIG"] = False` in your settings.

    For detailed instructions, please refer to the [Manual Setup](https://django-bird.readthedocs.io/configuration.html#manual-setup) section within the Configuration documentation.

## Getting Started

django-bird is a library for creating reusable components in Django. Here's how to create a simple `button` component.

Create a new directory named `bird` in your project's main templates directory. This will be the primary location for your components.

```bash
templates/
└── bird/
```

Inside the bird directory, create a new file named `button.html`. The filename determines the component's name.

```bash
templates/
└── bird/
    └── button.html
```

In `button.html`, create a simple HTML button. Use `{{ slot }}` to indicate where the main content will go.

```htmldjango
{# templates/bird/button.html #}
<button>
    {{ slot }}
</button>
```

To use your component in a Django template, use the `{% bird %}` templatetag. The content between `{% bird %}` and `{% endbird %}` becomes the `{{ slot }}` content.

```htmldjango
{% bird button %}
    Click me!
{% endbird %}
```

django-bird automatically recognizes components in the bird directory, so no manual registration is needed. When Django processes the template, django-bird replaces the `{% bird %}` tag with the component's HTML, inserting the provided content into the slot, resulting in:

```html
<button>
    Click me!
</button>
```

You now have a button component that can be easily reused across your Django project.
<!-- docs-content-end -->

## Documentation

django-bird includes features for creating flexible components, including:

- Passing attributes to components
- Named slots for organizing content within components
- Subcomponents for building complex component structures

For a full overview of the features and configuration options, please refer to the [documentation](https://bird.readthedocs.io).

## Motivation and Roadmap

### Roadmap

#### Static Asset Collection

#### Component Islands

#### Custom HTML Tag

#### Scoped CSS Styles

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
