# Variables in Components

Django Bird provides a way to manage local variables within components using the `bird:var` template tag. Similar to Django's built-in `{% with %}` tag, it allows you to create temporary variables, but with some key advantages:

- No closing tag required (unlike `{% with %}` which needs `{% endwith %}`)
- Variables are automatically cleaned up when the component finishes rendering
- Variables are properly scoped to each component instance
- Supports appending to existing values

## Basic Usage

The `bird:var` tag allows you to create and modify variables that are scoped to the current component. These variables are accessible through the `vars` context dictionary.

### Creating Variables

To create a new variable:

```django
{% bird:var name='value' %}
{{ vars.name }}  {# Outputs: value #}
```

### Appending to Variables

You can append to existing variables using the `+=` operator:

```django
{% bird:var greeting='Hello' %}
{% bird:var greeting+=' World' %}
{{ vars.greeting }}  {# Outputs: Hello World #}
```

If you append to a non-existent variable, it will be created:

```django
{% bird:var message+='World' %}
{{ vars.message }}  {# Outputs: World #}
```

## Variable Scope

Variables created with `bird:var` are:

- Local to the component where they are defined
- Isolated between different instances of the same component
- Not accessible outside the component
- Reset between renders

### Example of Scope Isolation

```django
{# button.html #}
{% bird:var count='1' %}
Count: {{ vars.count }}

{# template.html #}
{% bird button %}{% endbird %}
{% bird button %}{% endbird %}
Outside: {{ vars.count }}  {# vars.count is not accessible here #}
```

Each instance of the button component will have its own isolated `count` variable.

## Working with Template Variables

You can use template variables when setting values:

```django
{% bird:var greeting='Hello ' %}
{% bird:var greeting+=user.name %}
{{ vars.greeting }}  {# Outputs: Hello John #}
```

## Nested Components

Variables are properly scoped in nested components:

```django
{# outer.html #}
{% bird:var message='Outer' %}
{{ vars.message }}
{% bird inner %}{% endbird %}
{# vars.message still contains 'Outer' here #}

{# inner.html #}
{% bird:var message='Inner' %}
{{ vars.message }}  {# Contains 'Inner', doesn't affect outer component #}
```
