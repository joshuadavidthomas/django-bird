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
<!-- docs-motivation-begin -->

There are several excellent libraries for creating components in Django:

- [django-components](https://github.com/EmilStenstrom/django-components)
- [django-cotton](https://github.com/wrabit/django-cotton)
- [django-unicorn](https://github.com/adamghill/django-unicorn)
- [django-viewcomponent](https://github.com/rails-inspire-django/django-viewcomponent)
- [django-web-components](https://github.com/Xzya/django-web-components)
- [slippers](https://github.com/mixxorz/slippers)

In particular, django-components is full-featured and will take you far, while django-unicorn offers a novel approach to adding interactivity to Django projects without a full JavaScript framework.

> [!NOTE]
> Also worth mentioning is [django-template-partials](https://github.com/carltongibson/django-template-partials) from Carlton Gibson. While not a full component library, it allows you to define reusable template chunks in a Django template, providing a lightweight approach to template reusability.

**So, why another Django component library?**

These existing libraries offer valuable features, but many focus on Python-side component encapsulation. I saw an opportunity to explore a different approach of achieving encapsulation, from directly within Django templates.

Since I learned about the Locality of Behavior principle from [this essay](https://htmx.org/essays/locality-of-behaviour/) by HTMX's primary developer, I've been drawn to it. The principle suggests all code needed to understand a behavior should be in one place. Imagine a component library where a single template file could contain all necessary elements - structure, styles, and behavior - for a reusable component, similar to how [Svelte components](https://svelte.dev/docs/svelte-components) are defined, but for Django.

As a developer with strong opinions (sometimes loosely held 😄) about API design, I found myself at odds with existing libraries. None matched the template-centric, intuitive API I envisioned - one that embraced the single-file approach and Locality of Behavior within Django templates.

Initially, I considered contributing to existing libraries or wrapping one to add the functionality I wanted. However, I decided to create a new library for several reasons:

1. I didn't want to impose my opinion on anyone else's library or burden them with maintaining unwanted features.
2. While existing libraries' licenses allow for forking or wrapping, it's important to respect the original creators' work, especially for projects actively maintained by small teams or individual volunteers. Creating a new library avoids potential conflicts or misalignment with the original project's goals.
3. Healthy competition among libraries can drive innovation, benefiting all Django developers by encouraging continual improvement.
4. Recent innovations like [django-cotton](https://github.com/wrabit/django-cotton) and [dj-angles](https://github.com/adamghill/dj-angles) are pushing Django templates in exciting directions. I've also been inspired by developments outside Django. I've already mentioned Svelte's components, but there's also [Flux](https://fluxui.dev), a new Laravel component library by Caleb Porzio (creator of Livewire and Alpine.js). After watching [his Laracon US 2024 talk](https://www.youtube.com/watch?v=31pBMi0UdYE), I felt driven to bring similar simplicity to Django templates. Even if unsuccessful, this exploration can hopefully provide valuable insights and contribute to the evolution of Django's templating ecosystem.
5. Building from scratch lets me design the internals flexibly, experiment with new ideas and approaches for Django components without being constrained by existing architectures, and implement and test various concepts, iterating on what works best.

I'm excited and optimistic about django-bird's potential to offer a fresh perspective on component-based development in Django. It can complement the existing ecosystem of libraries, offering developers another option for their project needs.

<!-- docs-motivation-end -->
See the [ROADMAP](ROADMAP.md) for planned features and future direction of django-bird.

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
