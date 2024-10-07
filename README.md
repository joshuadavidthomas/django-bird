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

3. django-bird will automatically configure the necessary settings in your project.

    If you need to customize the configuration or prefer to set up django-bird manually, you can set `DJANGO_BIRD["ENABLE_AUTO_CONFIG"] = False` in your settings.

    For detailed instructions, please refer to the [Manual Setup](https://django-bird.readthedocs.io/configuration.html#manual-setup) section within the Configuration documentation.

## Getting Started

django-bird is a library for creating reusable components in Django. Let's create a simple button component to show the basics of how to use the library.

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

django-bird offers features for creating flexible components, such as:

- Passing attributes to components
- Named slots for organizing content within components
- Subcomponents for building complex component structures

For a full overview of the features and configuration options, please refer to the [documentation](https://bird.readthedocs.io).

## Motivation

Why another Django component library? There are already several excellent libraries for creating components in Django:

- [django-components](https://github.com/EmilStenstrom/django-components)
- [django-cotton](https://github.com/wrabit/django-cotton)
- [django-unicorn](https://github.com/adamghill/django-unicorn)
- [django-viewcomponent](https://github.com/rails-inspire-django/django-viewcomponent)
- [django-web-components](https://github.com/Xzya/django-web-components)
- [slippers](https://github.com/mixxorz/slippers)

In particular, django-components is full-featured and will take you far and django-unicorn offers a novel approach to adding interactivity to Django projects without relyihng on a full Javascript framework.

> [!NOTE]
> I also want to mention [django-template-partials](https://github.com/carltongibson/django-template-partials) by Carlton Gibson. While it is not a full component library, it allows you to define reusable inline template chunks, providing a lightweight approach to template reusability in Django.

Since I learned about Locality of Behavior in [this essay](https://htmx.org/essays/locality-of-behaviour/) written by the primary developer of HTMX, I've been drawn to it. This principle suggests all code needed to understand a behavior should be in one place. I'm inspired by Svelte's approach to components, where everything needed for the component - styles, scripts, and the main DOM - is in a single file.

Existing libraries offer valuable features, but many focus on Python-side component encapsulation. There is room for exploration in achieving a higher level of encapsulation directly within Django templates. I envisioned a component library where the template could contain all necessary elements - structure, styles, and behavior - in a single file.

As a developer with strong opinions (sometimes loosely held 😄) about API design, I imagined a component library with a template-centric interface that felt more intuitive to me.

While I considered contributing to these libraries to incorporate the features and API design I envisioned, or wrapping one to add functionality, I ultimately decided against these approaches for several reasons:

1. I didn't want to impose my opinion on anyone else's library or burden them with maintaining features they might not align with.
2. While existing libraries' licenses might allow for forking or wrapping, I believe it's important to respect the original creators' work, especially for projects maintained by small teams or individual volunteers. Creating a new library avoids potential conflicts or misalignments with the original project's goals.
3. Healthy competition among libraries can drive innovation across the ecosystem, benefiting all Django developers by encouraging continual improvement.
4. Recent innovations from libraries like [django-cotton](https://github.com/wrabit/django-cotton) and [dj-angles](https://github.com/adamghill/dj-angles) have started pushing Django templates in new, exciting directions. Inspired by these developments, I want to contribute my own ideas to the community. Even if unsuccessful, this exploration can hopefully provide valuable insights.
5. Building from scratch allows me to design the internals flexibly, experiment with new ideas and approaches for Django components without being constrained by existing architectures, and implement and test various concepts, iterating on what works best.

I'm excited and optimistic about the potential of django-bird to offer a fresh perspective on component-based development in Django. It can complement the existing ecosystem of component libraries, offering developers another option that better suits certain project needs or preferences.

See the [ROADMAP](ROADMAP.md) for planned features and future direction of django-bird.

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
