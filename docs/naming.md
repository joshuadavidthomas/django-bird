# Naming Components

Component names in django-bird are derived from their file locations and names within your templates directory. The naming system is flexible and supports both simple and complex component structures.

For detailed organization patterns and real-world examples, see the [Organizing Components](organization.md) documentation.

## Basic Naming

The simplest way to name a component is through its filename in the `bird` directory:

```bash
templates/
└── bird/
    └── button.html
```

This creates a component that can be used as:

```htmldjango
{% bird button %}
    Click me!
{% endbird %}
```

## Nested Names

Component names can include dots to represent directory structure:

```htmldjango
{% bird icon.arrow-down / %}
```

This maps to either a file path with dots (`icon.arrow-down.html`):

```bash
templates/
└── bird/
    └── icon.arrow-down.html
```

Or a nested directory structure (`icon/arrow-down.html`):

```bash
templates/
└── bird/
    └── icon/
        └── arrow-down.html
```

See [Organizing Components](organization.md) for detailed directory structure examples.

## Dynamic vs Literal Names

Component names can be either dynamic or literal:

```htmldjango
{# Dynamic name - resolves from context #}
{% with component_name="icon.arrow-down" %}
    {% bird component_name / %}
{% endwith %}

{# Literal name - always uses "button" #}
{% bird "button" / %}
{% bird 'button' / %}
```

When using an unquoted name, django-bird will attempt to resolve it from the template context. This is useful when the component choice needs to be determined at runtime in your Django view.

Using quoted names (single or double quotes) ensures the literal string is used as the component name, bypassing context resolution. This is useful when you want to ensure a specific component is always used, even if a variable with the same name exists in the context.

## Template Resolution

django-bird follows these rules when looking for component templates:

1. Searches custom directories specified in `COMPONENT_DIRS` setting, then the default `bird` directory
2. For a component in a directory (e.g., `accordion`), looks for:
   - `accordion/accordion.html`
   - `accordion/index.html`
   - `accordion.html`

This flexibility allows you to organize components according to your project's needs while maintaining consistent usage patterns.s
