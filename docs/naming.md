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

## Dynamic Names

Component names can be dynamic, using template variables:

```htmldjango
{% with component_name="icon.arrow-down" %}
    {% bird component_name / %}
{% endwith %}
```

This is particularly useful when the component choice needs to be determined at runtime in your Django view.

## Template Resolution

django-bird follows these rules when looking for component templates:

1. Searches custom directories specified in `COMPONENT_DIRS` setting, then the default `bird` directory
2. For a component in a directory (e.g., `accordion`), looks for:
   - `accordion/accordion.html`
   - `accordion/index.html`
   - `accordion.html`

This flexibility allows you to organize components according to your project's needs while maintaining consistent usage patterns.s
