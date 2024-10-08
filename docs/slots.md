# Slots

Slots allow you to define areas in your components where content can be inserted when the component is used. This feature provides flexibility and reusability to your components.

## Default Slot

Every component in django-bird has a default slot.

There are three ways to reference this default slot in your component template:

1. `{{ slot }}`
2. `{% bird:slot %}{% endbird:slot %}`
3. `{% bird:slot default %}{% endbird:slot %}`

These are all equivalent and will render the content placed between the opening and closing tags of your component when it's used. Let's look at each approach:

Using `{{ slot }}`:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button>
    {{ slot }}
</button>
```

Alternatively, you can use `{% bird:slot %}{% endbird:slot %}`:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button>
    {% bird:slot %}
    {% endbird:slot %}
</button>
```

Or, you can explicitly name the default slot with `{% bird:slot default %}{% endbird:slot %}`:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button>
    {% bird:slot default %}
    {% endbird:slot %}
</button>
```

When using any of these component templates, you would write:

```htmldjango
{% bird button %}
    Click me
{% endbird %}
```

And the output would be:

```html
<button>
    Click me
</button>
```

All three versions of the component template will produce the same output. Choose the syntax that you find most readable or that best fits your specific use case.

## Named Slots

In addition to the default slot, you can define named slots for more complex component structures. Named slots allow you to create more flexible and reusable components by specifying multiple areas where content can be inserted.

### Basic Usage

Here's a basic example of a component with a named slot:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button>
    {% bird:slot leading-icon %}
    {% endbird:slot %}
    {{ slot }}  {# This is the default slot #}
</button>
```

To use this component with a named slot:

```htmldjango
{% bird button %}
    {% bird:slot leading-icon %}
        <i class="icon-star"></i>
    {% endbird:slot %}
    Click me  {# This content goes into the default slot #}
{% endbird %}
```

This would output:

```html
<button>
    <i class="icon-star"></i>
    Click me
</button>
```

### Checking for Slot Content

django-bird provides a `slots` variable in the template context that allows you to check if a certain slot has been passed in. This can be useful for conditional rendering or applying different styles based on whether a slot is filled.

Here's an example of how you might use this:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button{% if slots.leading-icon %} class="with-icon"{% endif %}>
    {% if slots.leading-icon %}
        <span class="icon">
            {% bird:slot leading-icon %}
            {% endbird:slot %}
        </span>
    {% endif %}

    {{ slot }}
</button>
```

Now, you can use this component in different ways:

```htmldjango
{% bird button %}
    Click me
{% endbird %}
```

This would output:

```html
<button>
    Click me
</button>
```

But if you include the `leading-icon` slot:

```htmldjango
{% bird button %}
    {% bird:slot leading-icon %}
        <i class="icon-star"></i>
    {% endbird:slot %}

    Click me
{% endbird %}
```

It would output:

```html
<button class="with-icon">
    <span class="icon">
        <i class="icon-star"></i>
    </span>

    Click me
</button>
```

### Multiple Named Slots

You can define as many named slots as you need in a component. Here's an example with multiple named slots, demonstrating different ways to reference slot content:

```{code-block} htmldjango
:caption: templates/bird/card.html

<div class="card">
    {% if slots.header %}
        <div class="card-header">
            {% bird:slot header %}
            {% endbird:slot %}
        </div>
    {% endif %}

    <div class="card-body">
        {{ slot }}
    </div>

    {% if slots.footer %}
        <div class="card-footer">
            {{ slots.footer }}
        </div>
    {% endif %}
</div>
```

Note the different approaches used here:

1. For the `header`, we use the `{% bird:slot header %}{% endbird:slot %}` syntax.
2. For the main content, we use the `{{ slot }}` syntax for the default slot.
3. For the `footer`, we directly reference `{{ slots.footer }}`.

All these approaches are valid and will render the slot content. The choice between them often comes down to personal preference or specific use cases (e.g., needing to wrap the slot content in additional HTML).

This allows for very flexible usage of the component:

```htmldjango
{% bird card %}
    {% bird:slot header %}
        Card Title
    {% endbird:slot %}

    This is the main content of the card.

    {% bird:slot footer %}
        Card Footer
    {% endbird:slot %}
{% endbird %}
```

The output would be:

```html
<div class="card">
    <div class="card-header">
        Card Title
    </div>

    <div class="card-body">
        This is the main content of the card.
    </div>

    <div class="card-footer">
        Card Footer
    </div>
</div>
```

By using named slots and the `slots` dictionary, you can create highly adaptable components that can be used in a variety of contexts while maintaining a consistent structure. The ability to check for the existence of slot content (`{% if slots.header %}`) and to reference it directly (`{{ slots.footer }}`) provides great flexibility in how you structure your components.

## Fallback Content

You can provide default content for both named slots and the default slot that will fallback if nothing is passed in:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button>
    {% bird:slot leading-icon %}
        <span>
            Default icon
        </span>
    {% endbird:slot %}

    {% bird:slot %}
        Click me
    {% endbird:slot %}
</button>
```

If you use this component without providing content:

```htmldjango
{% bird button %}
{% endbird %}
```

It will output:

```html
<button>
    <span>
        Default icon
    </span>

    Click me
</button>
```

Remember, the default slot is always available, even when you define named slots. This allows for flexible component design that can adapt to different usage scenarios.
