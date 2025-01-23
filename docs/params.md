# Passing Parameters to Components

django-bird provides two ways to pass parameters to your components: attributes and properties. While attributes and properties may look similar when using a component, they serve different purposes.

Attributes are made available to your component template as a flattened string via the `{{ attrs }}` template context variable which can be used to apply HTML attributes to elements, while properties are accessible as individual values (e.g. `{{ props.variant }}`) that your component can use internally to control its rendering logic.

Note that these parameters are distinct from [Slots](slots.md) - they are used to configured how your component behaves or renders, while slots define where content should be inserted into your component's template.

For example, a button component might use properties to control its styling and attributes to set HTML attributes, while using slots to define its content:

```htmldjango
{% bird button variant="primary" data_analytics="signup" %}
    Click here  {# This content will go in the default slot #}
{% endbird %}
```

## Attributes

Attributes (i.e. `attrs`) let you pass additional HTML attributes to your components. This feature provides flexibility and customization without modifying the component template.

In your component template, the `{{ attrs }}` variable is a special variable that contains all the attributes passed to the component as a pre-rendered string. Unlike props which can be accessed individually, attributes are flattened into a single string ready to be inserted into an HTML element. The `{{ attrs }}` variable automatically handles both key-value attributes (like `class="btn"`) and boolean attributes (like `disabled`).

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

### Attribute Names

When rendering attributes, underscores in attribute names are automatically converted to hyphens. This is particularly useful for data attributes and other hyphenated HTML attributes:

```htmldjango
{% bird button data_analytics="signup" hx_get="/api/data" %}
    Load Data
{% endbird %}
```

This will render as:

```html
<button data-analytics="signup" hx-get="/api/data">
    Load Data
</button>
```

### Component ID Attribute

When the [`ENABLE_BIRD_ATTRS` setting](configuration.md#enable_bird_attrs) is enabled (the default), django-bird automatically adds data attributes to your components, available via the `{{ attrs }}` context variable.

The following attributes are included:

- `data-bird-<component_name>`: This attribute will contain the name of the component. This is not unique across component instances in the DOM.
- `data-bird-id`: This attribute contains a unique identifier that helps identify specific component instances in the DOM.

For example, for a component template like this:

```htmldjango
<button {{ attrs }}>
    {{ slot }}
</button>
```

And used like this:

```htmldjango
{% bird button class="btn" %}
    Click me
{% endbird %}
```

It will be rendered as:

```html
<button class="btn" data-bird-button data-bird-id="abc1234-1">
    Click me
</button>
```

The ID is automatically generated from a hash of the component's name and template content. It also contains a sequence counter that will increment for any uses of a component across a single template.

The above example button component template, used like this:

```htmldjango
{% bird button class="btn" %}
    Click me once
{% endbird %}
{% bird button class="btn" %}
    Click me twice
{% endbird %}
{% bird button class="btn" %}
    Click me three times a lady
{% endbird %}
```

Will be rendered like this, with the unique sequence numbers added to the component's hashed ID:

```html
<button class="btn" data-bird-button data-bird-id="abc1234-1">
    Click me once
</button>
<button class="btn" data-bird-button data-bird-id="abc1234-2">
    Click me twice
</button>
<button class="btn" data-bird-button data-bird-id="abc1234-3">
    Click me three times a lady
</button>
```

You can disable this feature globally by setting `ENABLE_BIRD_ATTRS = False` in your Django settings:

```python
DJANGO_BIRD = {
    "ENABLE_BIRD_ATTRS": False,
}
```

When disabled, no data attributes will be added to your components' `attrs` template context variable.

## Properties

Properties (i.e. `props`) allow you to define parameters that your component expects, with optional default values. Unlike attributes which are provided as a flattened string via `{{ attrs }}`, props are processed by the component and made available as individual values (e.g. `{{ props.variant }}`) that can be used to control rendering logic.

In your component template, props are defined using the `{% bird:prop %}` tag and accessed via the `{{ props }}` context variable. You can define as many props as needed using separate `{% bird:prop %}` tags. When a prop is defined, any matching attribute passed to the component will be removed from `{{ attrs }}` and made available in `{{ props }}` instead.

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

### Multiple Props

Components often need multiple props to control different aspects of their behavior. Each prop is defined with its own `{% bird:prop %}` tag:

```{code-block} htmldjango
:caption: templates/bird/button.html

{% bird:prop variant='primary' %}
{% bird:prop size='md' %}

<button
    class="btn btn-{{ props.variant }} btn-{{ props.size }}"
    {{ attrs }}
>
    {{ slot }}
</button>
```

Use the component by setting any combination of these props:

```htmldjango
{% bird button variant="secondary" size="lg" disabled=True %}
    Click me!
{% endbird %}
```

It will render as:

```html
<button class="btn btn-secondary btn-lg" disabled>
    Click me!
</button>
```

This approach of using separate tags for each prop makes it easier to expand the prop system in the future - for example, adding features like type validation or choice constraints while maintaining a clean syntax.

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

## Value Resolution

Both attributes and properties support literal (quoted) and dynamic (unquoted) values. This allows you to either hard-code values or resolve them from the template context.

The rules for value resolution are:

- Quoted values (`"value"` or `'value'`) are treated as literal strings
- Unquoted values are first attempted to be resolved from the template context
    - If resolution fails, the literal value is used as a fallback
- Boolean values can be passed directly (`disabled=True`) or as strings (`disabled="True"`)
- Both attributes and properties follow these same resolution rules

### Literal Values

Using quoted values ensures the exact string is used:

```htmldjango
{% bird button class="btn-primary" variant="large" disabled="true" %}
    Click me
{% endbird %}
```

Renders as:

```html
<button class="btn-primary" variant="large" disabled="true">Click me</button>
```

### Dynamic Values

Unquoted values are resolved from the template context:

```htmldjango
{% bird button class=button_class variant=size disabled=is_disabled %}
    Click me
{% endbird %}
```

With this context:

```python
{
    "button_class": "btn-secondary",
    "size": "small",
    "is_disabled": True,
}
```

Renders as:

```html
<button class="btn-secondary" variant="small" disabled>Click me</button>
```

If an unquoted value cannot be resolved from the context, it falls back to using the literal string:

```htmldjango
{% bird button class=undefined_class %}
    Click me
{% endbird %}
```

With empty context, renders as:

```html
<button class="undefined_class">Click me</button>
```

You can also access nested attributes using dot notation:

```htmldjango
{% bird button class=theme.button.class disabled=user.is_inactive %}
    Click me
{% endbird %}
```

With this context:

```python
{
    "theme": {
        "button": {
            "class": "themed-button",
        }
    },
    "user": {
        "is_inactive": True,
    },
}
```

Renders as:

```html
<button class="themed-button" disabled>Click me</button>
```

## Context Isolation

By default, components have access to their parent template's context. This means variables defined in the parent template are available inside the component.

You can use the `only` keyword to prevent a component from accessing its parent context:

```htmldjango
{% bird button only %}
    Click me
{% endbird %}
```

When `only` is used:

- The component cannot access variables from the parent context
- Props, slots, and other component-specific context still work normally
- Default values in the component template will be used when parent context variables are not available

### Examples

Without `only`, components can access parent context:

```htmldjango
{# Parent template with user in context #}
{% bird button %}
    {{ user.name }}  {# Will render "John" #}
{% endbird %}
```

With `only`, parent context is isolated:

```htmldjango
{# Parent template with user in context #}
{% bird button only %}
    {{ user.name|default:"Anonymous" }}  {# Will render "Anonymous" #}
{% endbird %}
```

Props and slots still work with `only`:

```htmldjango
{% bird button variant="primary" only %}
    {% bird:slot prefix %}→{% endbird:slot %}
    Submit
{% endbird %}
```
