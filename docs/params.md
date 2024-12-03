# Passing Parameters to Components

django-bird provides two ways to pass parameters to your components: attributes and properties. While attributes and properties may look similar when using a component, they serve different purposes. Attributes are passed directly through to the underlying HTML elements, while properties are parameters that your component can use internally to control its rendering logic,

Note that these parameters are distinct from [Slots](slots.md) - they are used to configured how your component behaves or renders, while slots define where content should be inserted into your component's template.

For example, a button component might use properties to control its styling and attributes to set HTML attributes, while using slots to define its content:

```htmldjango
{% bird button variant="primary" data-analytics="signup" %}
    Click here  {# This content will go in the default slot #}
{% endbird %}
```

## Attributes

Attributes (i.e. `attrs`) let you pass additional HTML attributes to your components. This feature provides flexibility and customization without modifying the component template.

In your component template, the `{{ attrs }}` variable is a special variable that contains all the attributes passed to the component. It automatically handles both key-value attributes (like `class="btn"`) and boolean attributes (like `disabled`).

### Basic Usage

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

### Multiple Attributes

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

## Properties

Properties (i.e. `props`) allow you to define parameters that your component expects, with optional default values. Unlike attributes which pass through directly to the HTML, props are processed by the component and can be used to control rendering logic.

In your component template, props are defined using the `{% bird:prop %}` tag and accessed via the `{{ props }}` context variable. When a prop is defined, any matching attribute passed to the component will be removed from `{{ attrs }}` and made available in `{{ props }}` instead.

### Basic Usage

Here's a simple example of a button component that uses props:

```{code-block} htmldjango
:caption: templates/bird/button.html

{% bird:prop variant='primary' %}
<button class="btn btn-{{ props.variant }}" {{ attrs }}>
    {{ slot }}
</button>
```

Use this component and override the default variant like this:

```htmldjango
{% bird button variant="secondary" id="secondary-button" %}
    Click me!
{% endbird %}
```

It will render as:

```html
<button class="btn btn-secondary" id="secondary-button">
    Click me!
</button>
```

Notice how this works:

- The `variant` attribute is removed from `attrs` because it matches a defined prop
- Its value "secondary" is made available as `props.variant`
- The `id` attribute remains in `attrs` since it's not defined as a prop
- The final HTML only includes `variant`'s value as part of the class name, while `id` appears as a direct attribute

This separation allows you to use props to control your component's logic while still accepting arbitrary HTML attributes.

### Props with Defaults

Props can be defined with or without default values:

```htmldjango
{% bird:prop id %}                 {#  No default value  #}
{% bird:prop variant='primary' %}  {# With default value #}
<button 
    id="{{ props.id }}"
    class="btn btn-{{ props.variant }}"
    {{ attrs }}
>
    {{ slot }}
</button>
```

When used, props will take their value from either the passed attribute or fall back to their default:

```htmldjango
{% bird button variant="secondary" %}
    Submit
{% endbird %}
```

This will render as:

```html
<button id="" class="btn btn-secondary">
    Submit
</button>
```

```{note}
Props defined without a default value will render as an empty string if no value is provided when using the component. This behavior may change in a future version to either require default values or handle undefined props differently.
```
