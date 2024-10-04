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

## Roadmap

Here's a roadmap of features I'm considering for django-bird:

### Static Asset Collection

This is table stakes for a modern Django template component library. You should be able to define CSS and JS for a component and have it loaded automatically when you use that component.

Unlike django-components, which uses the Django forms library pattern with a `class Media` declaration, I want to allow defining styles and scripts within a single component file. django-bird will then collect and compile these assets, streamlining the whole process.

### Component Islands

Ever since I tried Astro and discovered their concept of "Islands" (which they popularized but didn't invent), I've wanted to bring this to Django.

If you're new to component islands, think of it as fancy lazy-loading. You can set different triggers for when a component's JS assets load (on page load, on idle, on scroll into view). When that event fires, only the necessary assets are loaded.

There's a neat library from the 11ty team called is-land that could work well here. I'll probably start by integrating it directly, but after looking at their source code, I might end up bringing it in and customizing it for django-bird's specific needs.

### Custom HTML Tag

I'm a huge fan of the approaches taken by libraries like [django-cotton](https://github.com/wrabit/django-cotton), [dj-angles](https://github.com/adamghill/dj-angles), and Laravel's [Flux](https://fluxui.dev). They let you use custom HTML-like elements that compile down to native templatetags during loading.

This gives you the full power of Django's template language, but in a much nicer package. Compare [this django-allauth template](https://github.com/pennersr/django-allauth/blob/f03ff4dd48e5b1680a57dca56617bf94c928f2cf/allauth/templates/account/email.html) with [these django-cotton examples](https://github.com/wrabit/django-cotton#walkthrough). The allauth template, while powerful, is a mess of tags that barely resembles HTML. The cotton templates, on the other hand, look like clean, custom web elements.

After working with devs from the JavaScript world and using a handful of JavaScript frameworks myself, Django templates can feel ancient compared to JSX. A custom HTML tag approach won't solve all these issues, but it's a step in the right direction.

### Scoped CSS Styles

I love how Svelte and other JS frameworks let you use a simple `<style>` tag with broad selectors (`p` instead of `.card-body`, `button` instead of `.submit-btn`), then scope those styles to just that component. While I'm a Tailwind CSS fan, having this escape hatch for quick style tweaks would be fantastic.

### Integration with Tailwind CSS

Hot 🔥 take: ditch most of Tailwind's atomic classes and write your styles in a CSS file (shocking, I know!), but process it with Tailwind. This gives you modern CSS power without the atomic class juggling, plus you still get to use Tailwind's awesome design system -- which in my mind is _the_ reason to use Tailwind CSS. I could take or leave the atomic styles, but that design system I cannot develop without.

I'd love for django-bird components to support this workflow, letting you write clean, Tailwind-processed styles right in your components.

## License

`django-bird` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
