# Roadmap

Below are a bunch of features I'd like to bring to django-bird.

I have included code snippets where applicable, but they are back-of-the-napkin sketches of potential APIs -- subject to change if and when the feature is actually introduced.

## Static Asset Collection 🏗️

> [!NOTE]
> django-bird [v0.6.0](https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.6.0) introduced automatic asset management via `{% bird:css %}` and `{% bird:js %}` templatetags. The current implementation automatically discovers and loads CSS and JS files that match your component names:
>
> ```bash
> templates/bird/button/
> ├── button.css     # Automatically loaded by {% bird:css %}
> ├── button.html    # Component template
> └── button.js      # Automatically loaded by {% bird:js %}
> ```
>
> Future versions should eventually add support for inline styles and scripts with proper component scoping, compilation, and bundling.
>
> See the [docs](https://django-bird.readthedocs.io/en/latest/assets.html) for more information.

This is table stakes for a modern Django template component library. The goal is to allow you to define CSS and JS for a component and have it loaded automatically when you use that component.

Unlike django-components, which uses the Django forms library pattern with a `class Media` declaration, the idea is to allow defining styles and scripts within a single component file, or adjacent to a component. django-bird would then collect and compile these assets, streamlining the whole process.

Here's a potential example of how you might define a button component with inline styles and scripts:

```htmldjango
{# templates/bird/button.html #}
<button>
    {{ slot }}
</button>
<style>
    button {
        background-color: red;
        padding: 10px 20px;
        color: white;
        border: none;
        cursor: pointer;
    }
</style>
<script>
    $bird.addEventListener('click', () => {
        alert('This specific button was clicked!');
    });
</script>
```

The `$bird` variable in the JavaScript is a potential special identifier that could be used to scope the script to the specific component instance.

Alternatively, you could potentially separate the styles and scripts into their own files. This is similar to how django-components handles CSS and JS assets.

```htmldjango
{# templates/bird/button.html #}
<button>
    {{ slot }}
</button>
```

```css
/* templates/bird/button.css */
button {
  background-color: red;
  padding: 10px 20px;
  color: white;
  border: none;
  cursor: pointer;
}
```

```javascript
// templates/bird/button.js
$bird.addEventListener('click', () => {
  alert('This specific button was clicked!');
});
```

To use this component and include its assets in your template, the API might look something like this:

```htmldjango
<html>
    <head>
        {% django_bird_css %}
    </head>
    <body>
        {% bird button %}
            Click me
        {% endbird %}

        {% django_bird_js %}
    </body>
</html>
```

In this conceptual setup, `{% django_bird_css %}` and `{% django_bird_js %}` would automatically include the collected and compiled CSS and JavaScript for all components used in the template.

To give you an idea of what the final compiled output might look like, here's a hypothetical example of the HTML that could be generated, with the CSS [scoped](#scoped-css-styles) to just the button component:

```htmldjango
<html>
    <head>
        <style>
            [data-bird-id="button-1"] {
                background-color: red;
                padding: 10px 20px;
                color: white;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <button data-bird-id="button-1">
            Click me
        </button>

        <script>
            (function() {
                const $bird = document.querySelector('[data-bird-id="button-1"]');
                $bird.addEventListener('click', () => {
                    alert('This specific button was clicked!');
                });
            })();
        </script>
    </body>
</html>
```

> **Update, 2024-12-03**
> The current implementation handles basic asset discovery and loading, but future enhancements will include:
>
> - Inline style and script support with component scoping
> - Asset compilation and bundling
> - The `$bird` variable for component-specific JavaScript
> - CSS scoping via data attributes

## Overriding Default Attributes ✅

> [!NOTE]
> This was added in django-bird [v0.3.0](https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.3.0) via the `{% bird:props %}` templatetag. There are now two ways to define parameters passed in to django-bird components: attributes and properties.

Similiarly, this is table stakes for a modern Django component library. You should be able to set default attributes in your component and allow them to be overridden:

```htmldjango
{# templates/bird/input.html #}
<input type="text" class="form-input" {{ attrs }} />
```

When using this component:

```htmldjango
{% bird input type="email" class="special-input" / %}
```

It will render as:

```html
<input type="email" class="special-input" />
```

This feature would allow the usage type and class attributes to override the component template defaults, providing even more flexibility in component design and usage.

## Tailwind CSS Class Merging

I also want to explore Tailwind CSS class merging functionality, similar to the `tailwind-merge` NPM package. This feature would allow for intelligent combination of Tailwind CSS classes, resolving conflicts and producing optimal class strings.

Here's an example of how this might work in django-bird:

```htmldjango
{# templates/bird/button.html #}
<button class="{% tw_merge attrs.class 'px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded' %}">
    {{ slot }}
</button>
```

When using this component:

```htmldjango
{% bird button class="bg-red-500 px-6" %}
    Click me
{% endbird %}
```

It would render as:

```html
<button class="px-6 py-2 bg-red-500 hover:bg-blue-600 text-white rounded">
    Click me
</button>
```

In this example, `tw_merge` is a custom templatetag that merges the passed classes with the default classes.

It will be able to intelligently handle conflicts:

- `px-6` from the passed classes overrides `px-4` from the defaults
- `bg-red-500` overrides `bg-blue-500`
- Other classes from the defaults (`py-2`, `hover:bg-blue-600`, `text-white`, `rounded`) are preserved

There are also these possibilities:

1. **Built-in Merging**: Instead of a dedicated templatetag, what if the library could handle this in the core? Though, to be honest, I'm not sure what that would look like.

2. **Importance Marking**: Some component libraries, like [Flux](https://fluxui.dev) for Laravel, use a different approach. They require users to prefix any Tailwind classes they want to override with `!`, marking them as important. For example:

   ```htmldjango
   {% bird button class="!bg-red-500 !px-6" %}
       Click me
   {% endbird %}
   ```

   This method provides explicit control over which classes should take precedence.

## Component Islands

Ever since I tried Astro and discovered their concept of "Islands" (which they popularized but didn't invent), I've wanted to bring this to Django.

If you're new to component islands, think of it as fancy lazy-loading. You can set different triggers for when a component's JS assets load (on page load, on idle, on scroll into view). When that event fires, only the necessary assets are loaded.

There's a neat library from the 11ty team called [is-land](https://github.com/11ty/is-land) that could work well here. It has been a while since it has had any updates, which is not necessarily a bad thing. The 11ty team may consider it feature-complete, or perhaps priorities have shifted? Either way I'll probably start by using the library as-is, but I may explore bringing the source directly in and customizing it for django-bird's specific needs.

Here's how the API for component islands might look in django-bird:

```htmldjango
{% bird button on="load" %}
    This button loads... on load
{% endbird %}

{% bird button on="idle" %}
    This button loads after page load
{% endbird %}

{% bird button on="visible" %}
    This button loads when scrolled into view
{% endbird %}
```

In this example, we're using an `on` attribute to specify when each button's JavaScript should be loaded and executed. This approach could significantly improve page load times and performance, especially for pages with many interactive components.

## Custom HTML Tag

I'm a huge fan of the approaches taken by libraries like [django-cotton](https://github.com/wrabit/django-cotton), [dj-angles](https://github.com/adamghill/dj-angles), and Laravel's [Flux](https://fluxui.dev). They let you use custom HTML-like elements that compile down to native templatetags during loading.

This gives you the full power of Django's template language, but in a much nicer package. Compare [this django-allauth template](https://github.com/pennersr/django-allauth/blob/f03ff4dd48e5b1680a57dca56617bf94c928f2cf/allauth/templates/account/email.html) with [these django-cotton examples](https://github.com/wrabit/django-cotton#walkthrough). The allauth template, while powerful, is a mess of tags that barely resembles HTML. The cotton templates, on the other hand, look like clean, custom web elements.

After working with devs from the JavaScript world and using a handful of JavaScript frameworks myself, Django templates can feel ancient compared to JSX. A custom HTML tag approach could offer a more familiar and readable syntax for component-based development in Django, bridging the gap between traditional Django templates and modern frontend practices.

Here's a comparison of how a button component might be used with the current django-bird syntax and a potential custom HTML tag syntax:

```htmldjango
{% bird button %}
    Click me
{% endbird %}

<bird:button>
    Click me
</bird:button>
```

## Scoped CSS Styles

I love how Svelte and other JS frameworks let you use a simple `<style>` tag with broad selectors (`p` instead of `.card-body`, `button` instead of `.submit-btn`), then scope those styles to just that component. While I'm a Tailwind CSS fan, having this escape hatch for quick style tweaks would be fantastic.

Here's how a component with scoped styles might look in django-bird:

```htmldjango
{# templates/bird/button.html #}
<button>
    {{ slot }}
</button>
<style>
    button {
        background-color: red;
    }
</style>
```

You would use this component in your template like this:

```htmldjango
<html>
    <head>
        {% django_bird_css %}
    </head>
    <body>
        {% bird button %}
            Click me
        {% endbird %}
    </body>
</html>
```

And here's a potential example of how django-bird might compile this to ensure the styles are scoped to just this component:

```htmldjango
<html>
    <head>
        <style>
            [data-bird-id="button-1"] {
                background-color: red;
            }
        </style>
    </head>
    <body>
        <button data-bird-id="button-1">
            Click me
        </button>
    </body>
</html>
```

Note: this has significant overlap with [static asset collection](#static-asset-collection).

## CSS Styles Processed with Tailwind CSS

Hot 🔥 take: if you're using Tailwind, you should ditch most of Tailwind's atomic classes and write your styles in a CSS file (shocking, I know!), but process it with Tailwind. This gives you modern CSS power without the atomic class juggling, plus you still get to use Tailwind's awesome design system -- which in my mind is _the_ reason to use Tailwind CSS. I could take or leave the atomic styles, but that design system I cannot develop without.

I'd love for bird components to support this workflow, letting you write clean, Tailwind-processed styles right in your components.

Here's how a button component using Tailwind's design system might look in django-bird:

```htmldjango
{# templates/bird/button.html #}
<button>
    {{ slot }}
</button>
<style>
    button {
        background-color: theme("colors.red.500");
    }
</style>
```
