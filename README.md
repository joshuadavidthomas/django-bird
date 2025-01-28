<!-- docs-intro-begin -->
# django-bird

[![PyPI](https://img.shields.io/pypi/v/django-bird)](https://pypi.org/project/django-bird/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-bird)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1%20%7C%205.2-%2344B78B?labelColor=%23092E20)
<!-- https://shields.io/badges -->
<!-- django-4.2 | 5.0 | 5.1 | 5.2-#44B78B -->
<!-- labelColor=%23092E20 -->

High-flying components for perfectionists with deadlines.

<!-- docs-intro-end -->
> [!CAUTION]
> This is an experimental, alpha attempt at a different approach to defining components in Django templates. It is not suitable for production use yet.

<!-- docs-content-begin -->
## Requirements

- Python 3.10, 3.11, 3.12, 3.13
- Django 4.2, 5.0, 5.1, 5.2

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

In `button.html`, create a simple HTML button. Use `{{ slot }}` to indicate where the main content will go. We will also define a component property via the `{% bird:prop %}` templatetag and add `{{ attrs }}` for passing in arbitrary HTML attributes.

```htmldjango
{# templates/bird/button.html #}
{% bird:prop class="btn" %}
{% bird:prop data_attr="button" %}

<button class="{{ props.class }}" data-attr="{{ props.data_attr }}" {{ attrs }}>
    {{ slot }}
</button>
```

To use your component in a Django template, use the `{% bird %}` templatetag. The content between `{% bird %}` and `{% endbird %}` becomes the `{{ slot }}` content. Properties and attributes are set as parameters on the `{% bird %}` tag itself.

```htmldjango
{% bird button class="btn-primary" disabled=True %}
    Click me!
{% endbird %}
```

django-bird automatically recognizes components in the bird directory, so no manual registration is needed. When Django processes the template, django-bird replaces the `{% bird %}` tag with the component's HTML, inserting the provided content into the slot, resulting in:

```html
<button class="btn-primary" data-attr="button" disabled>
    Click me!
</button>
```

You now have a button component that can be easily reused across your Django project.
<!-- docs-content-end -->

## Documentation

django-bird offers features for creating flexible components, such as:

- [Defining and registering components](https://django-bird.readthedocs.io/en/latest/naming.html) entirely within Django templates, without writing a custom templatetag
- Passing [attributes and properties](https://django-bird.readthedocs.io/en/latest/params.html) to components
- [Named slots](https://django-bird.readthedocs.io/en/latest/slots.html#named-slots) for organizing content within components
- [Subcomponents](https://django-bird.readthedocs.io/en/latest/organization.html) for building complex component structures
- Automatic [asset management](https://django-bird.readthedocs.io/en/latest/assets.html) for component CSS and JavaScript files

For a full overview of the features and configuration options, please refer to the [documentation](https://django-bird.readthedocs.io).

## Motivation

<!-- docs-motivation-begin -->
Several excellent libraries for creating components in Django exist:

- [django-components](https://github.com/EmilStenstrom/django-components)
- [django-cotton](https://github.com/wrabit/django-cotton)
- [django-unicorn](https://github.com/adamghill/django-unicorn)
- [django-viewcomponent](https://github.com/rails-inspire-django/django-viewcomponent)
- [django-web-components](https://github.com/Xzya/django-web-components)
- [slippers](https://github.com/mixxorz/slippers)

> [!NOTE]
> Also worth mentioning is [django-template-partials](https://github.com/carltongibson/django-template-partials) from Carlton Gibson. While not a full component library, it allows defining reusable chunks in a Django template, providing a lightweight approach to reusability.

These libraries are excellent in their own right, each solving specific problems in innovative ways: django-components is full-featured and will take most people far with custom components, django-unicorn offers a novel approach to adding interactivity without a full JavaScript framework, and django-cotton has a new way of defining custom components that has me very excited.

**So, why another Django component library?**

Most of the ones above focus on defining components on the Python side, which works for many use cases. For those focusing on the HTML and Django template side, they have made significant strides in improving the developer experience. However, as a developer with strong opinions (sometimes loosely held 😄) about API design, I wanted a different approach.

After watching Caleb Porzio's [2024 Laracon US talk](https://www.youtube.com/watch?v=31pBMi0UdYE) introducing [Flux](https://fluxui.dev), I could not shake the desire to bring something similar to Django. While there are plenty of libraries such as Shoelace or UI kits designed for use in any web application, and tools like SaaS Pegasus for whole Django project generation, I couldn't find a well-polished component library solely dedicated to Django templates with the level of polish that Flux has for Laravel.

Initially, I considered contributing to existing libraries or wrapping one to add the functionality I wanted. However, I decided to create a new library for several reasons:

1. I wanted to respect the hard work of existing maintainers and avoid burdening them with features that may not align with their project's goals.
2. While wrapping an existing library might have been technically feasible and okay license-wise, it didn't feel right to build an entire component system on top of someone else's work, especially for a project I might want to develop independently in the future.
3. Building something new gives me the freedom to fully control the direction and architecture, without being constrained by design choices made in other libraries.
4. Healthy competition among libraries helps drive innovation, and I see this as an opportunity to contribute to the broader Django ecosystem.
5. Recent libraries like [django-cotton](https://github.com/wrabit/django-cotton) and [dj-angles](https://github.com/adamghill/dj-angles) are pushing Django templates in new and exciting directions and I wanted to join in on the fun. 😄

It's very early days for django-bird. What you see here is laying the foundation for a template-centric approach to Django components. The current implementation focuses on core functionality, setting the stage for future features and enhancements.
<!-- docs-motivation-end -->

See the [ROADMAP](ROADMAP.md) for planned features and the future direction of django-bird.

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
