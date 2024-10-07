# Attributes

Attributes let you pass additional HTML attributes to your components. This feature provides flexibility and customization without modifying the component template.

In your component template, the `{{ attrs }}` variable is a special variable that contains all the attributes passed to the component. It automatically handles both key-value attributes (like `class="btn"`) and boolean attributes (like `disabled`).

## Basic Usage

Here's a simple example of a button component that accepts attributes:

```{code-block} htmldjango
:caption: templates/bird/button.html

<button {{ attrs }}>
    {{ slot }}
</button>
```

Use this component and pass attributes like this:

```htmldjango
{% bird button class="btn" %}
    Click me!
{% endbird %}
```

It will render as:

```html
<button class="btn">
    Click me!
</button>

```

## Multiple Attributes

You can pass multiple attributes to a component:

```htmldjango
{% bird button class="btn btn-primary" id="submit-btn" disabled %}
    Submit
{% endbird %}
```

This will render as:

```html
<button class="btn btn-primary" id="submit-btn" disabled>
    Submit
</button>
```
