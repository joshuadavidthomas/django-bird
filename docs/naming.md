# Naming Components

Component names in django-bird are derived from their file locations and names within your templates directory. The naming system is flexible and supports both simple and complex component structures.

For more complex component structures and organization patterns, see the [Organizing Components](organization.md) documentation.

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

Component names can include dots to represent directory structure. A component nested with this directory structure:

```bash
templates/
└── bird/
    └── icon/
        └── arrow-down.html
```

Translates to using the component with:

```htmldjango
{% bird icon.arrow-down / %}
```

## Dynamic Names

Component names can be dynamic, using template variables:

```htmldjango
{% with component_name="icon.arrow-down" %}
    {% bird component_name / %}
{% endwith %}
```

This is particularly useful when the component choice needs to be determined at runtime in your Django view.

## Name Resolution

When resolving component names, django-bird searches in this order:

1. Custom directories specified in `COMPONENT_DIRS` setting
2. The default `bird` directory

For a component named `accordion`:

```bash
templates/
├── components/  # Custom directory via DJANGO_BIRD["COMPONENT_DIRS"] setting
│   └── accordion.html
└── bird/
    └── accordion.html
```

The version in `components/` takes precedence over the one in `bird/`.

## Index Files

Following the web convention where `example.com/blog/` automatically serves `example.com/blog/index.html`, django-bird will look for either:

- `<name>/<name>.html`
- `<name>/index.html`

```bash
templates/
└── bird/
    └── accordion/
        ├── index.html  # Primary accordion component
        ├── item.html
        └── content.html
```

The component `{% bird accordion %}` will resolve to `index.html`.
