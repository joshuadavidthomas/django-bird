# Variables in Components

django-bird provides a way to manage local variables within components using the `{% bird:var %}` template tag. Similar to Django's built-in `{% with %}` tag, it allows you to create temporary variables, but with some key advantages:

- No closing tag required (unlike `{% with %}` which needs `{% endwith %}`)
- Variables are automatically cleaned up when the component finishes rendering
- Variables are properly scoped to each component instance
- Supports appending to existing values

## Basic Usage

The `{% bird:var %}` tag allows you to create and modify variables that are scoped to the current component. These variables are accessible through the `vars` context dictionary.

### Creating Variables

To create a new variable, use the assignment syntax:

```htmldjango
{% bird:var name='value' %}

{{ vars.name }}  {# Outputs: value #}
```

### Overwriting and Clearing Variables

You can overwrite an existing variable by assigning a new value:

```htmldjango
{% bird:var counter='1' %}

{{ vars.counter }}  {# Outputs: 1 #}

{% bird:var counter='2' %}

{{ vars.counter }}  {# Outputs: 2 #}
```

To reset/clear a variable, set it to None:

```htmldjango
{% bird:var message='hello' %}

{{ vars.message }}  {# Outputs: hello #}

{% bird:var message=None %}

{{ vars.message }}  {# Variable is cleared #}
```

Alternatively, you can use explicit cleanup with `{% endbird:var %}` - see [Explicit Variable Cleanup](#explicit-variable-cleanup) for details.

### Appending to Variables

The `+=` operator lets you append to existing variables:

```htmldjango
{% bird:var greeting='Hello' %}
{% bird:var greeting+=' World' %}

{{ vars.greeting }}  {# Outputs: Hello World #}
```

If you append to a non-existent variable, it will be created:

```htmldjango
{% bird:var message+='World' %}

{{ vars.message }}  {# Outputs: World #}
```

## Variable Scope

Variables created with `{% bird:var %}` are:

- Local to the component where they are defined
- Isolated between different instances of the same component
- Not accessible outside the component
- Reset between renders

```{code-block} htmldjango
:caption: templates/bird/button.html

{% bird:var count='1' %}

Count: {{ vars.count }}
```

```{code-block} htmldjango
:caption: template.html

{% bird button %}{% endbird %} {# Count: 1 #}
{% bird button %}{% endbird %} {# Count: 1 #}

Outside: {{ vars.count }}  {# vars.count is not accessible here #}
```

Each instance of the button component will have its own isolated `count` variable.

### Explicit Variable Cleanup

While variables are automatically cleaned up when a component finishes rendering, you can explicitly clean up variables using the `{% endbird:var %}` tag:

```htmldjango
{% bird:var message='Hello' %}

{{ vars.message }}  {# Outputs: Hello #}

{% endbird:var message %}

{{ vars.message }}  {# Variable is now cleaned up #}
```

This can be useful when you want to ensure a variable is cleaned up at a specific point in your template, rather than waiting for the component to finish rendering.

You can clean up multiple variables independently:

```htmldjango
{% bird:var x='hello' %}
{% bird:var y='world' %}

{{ vars.x }} {{ vars.y }}  {# Outputs: hello world #}

{% endbird:var x %}

{{ vars.x }} {{ vars.y }}  {# Outputs: world (x is cleaned up) #}

{% endbird:var y %}

{{ vars.x }} {{ vars.y }}  {# Both variables are now cleaned up #}
```

## Working with Template Variables

You can use template variables when setting values:

```htmldjango
{% bird:var greeting='Hello ' %}
{% bird:var greeting+=user.name %}

{{ vars.greeting }}  {# Outputs: Hello John #}
```

## Nested Components

Variables are properly scoped in nested components:

```{code-block} htmldjango
:caption: templates/bird/outer.html

{% bird:var message='Outer' %}

{{ vars.message }}

{% bird inner %}{% endbird %}

{{ vars.message }} {# vars.message still contains 'Outer' here #}
```

```{code-block} htmldjango
:caption: templates/bird/inner.html

{% bird:var message='Inner' %}

{{ vars.message }}  {# Contains 'Inner', doesn't affect outer component #}
```
