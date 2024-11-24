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

## Component Directories

django-bird searches for component templates in multiple locations, following a specific precedence order:

1. Custom directories specified in `COMPONENT_DIRS` setting
2. The default `bird` directory

For example, with a component named `accordion`:

```bash
templates/
├── components/  # Custom directory via DJANGO_BIRD["COMPONENT_DIRS"] setting
│   └── accordion.html
└── bird/
    └── accordion.html
```

The version in `components/` takes precedence over the one in `bird/`.

## Primary Name

django-bird supports two standard naming patterns for your component's main template file, similar to how web servers handle directory indexes (e.g. `example.com/blog/index.html` automatically being served at `example.com/blog/`).

For a component named `accordion`, you can name the main template file either:

```bash
templates/
└── bird/
    └── accordion/
        └── index.html
```

Or alternatively:

```bash
templates/
└── bird/
    └── accordion/
        └── accordion.html
```

In both cases, the template tag `{% bird accordion %}` will find and render the component. You can choose whichever naming convention better matches your project's style.
