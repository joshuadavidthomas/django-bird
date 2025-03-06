# CSS and JavaScript Assets

django-bird automatically discovers and manages CSS and JavaScript assets for your components.

## Asset Discovery

Assets are discovered based on file names matching your component template:

```bash
templates/bird/
├── button.css
├── button.html
└── button.js
```

The library looks for `.css` and `.js` files with the same name as your component template.

You can also organize components in their own directories. The library will find assets as long as they match the component name and are in the same directory as the template:

```bash
templates/bird/button/
├── button.css
├── button.html
└── button.js
```

This organization can be particularly useful when components have multiple related files or when you want to keep component code isolated. See [Template Resolution](naming.md#template-resolution) for more information and [Organization](organization.md) for different ways to structure your components and their assets.

## Using Assets

django-bird provides two templatetags for automatically loading your CSS and Javascript assets into your project's templates:

- `{% bird:css %}`
- `{% bird:js %}`

To include component assets in your templates, add the templatetags to your base template:

```htmldjango
<!DOCTYPE html>
<html>
    <head>
        {% bird:css %}  {# Includes CSS from all components used in template #}
    </head>
    <body>
        {% block content %}{% endblock %}
        {% bird:js %}   {# Includes JavaScript from all components used in template #}
    </body>
</html>
```

The asset tags will automatically:

- Find all components used in the template (including extends and includes)
- Collect their associated assets
- Output the appropriate HTML tags

For example, if your template uses components with associated assets:

```htmldjango
{% bird button %}Click me{% endbird %}
{% bird alert %}Warning!{% endbird %}
```

The asset tags will render:

```html
{# {% bird:css %} renders: #}
<link rel="stylesheet" href="/static/django_bird/bird/button.css">
<link rel="stylesheet" href="/static/django_bird/bird/alert.css">

{# {% bird:js %} renders: #}
<script src="/static/django_bird/bird/button.js"></script>
<script src="/static/django_bird/bird/alert.js"></script>
```

Assets are automatically deduplicated, so each component's assets are included only once even if the component is used multiple times in your templates. Only assets from components actually used in the template (or its parent templates) will be included - unused components' assets won't be loaded, keeping your pages lean.

## Template Inheritance

Assets are collected from all components used in your template hierarchy:

```{code-block} htmldjango
:caption: base.html

<!DOCTYPE html>
<html>
    <head>
        {% bird:css %}  {# Gets CSS from both nav and content components #}
    </head>
    <body>
        {% bird nav %}{% endbird %}
        {% block content %}{% endblock %}
        {% bird:js %}
    </body>
</html>
```

```{code-block} htmldjango
:caption: page.html

{% extends "base.html" %}

{% block content %}
    {% bird content %}
        Page content here
    {% endbird %}
{% endblock %}
```

The `{% bird:css %}` tag will include CSS and the `[% bird:js %}` tag will include JavaScript from both the `nav` and `content` components.

## Serving Assets

### Using the Staticfiles Finder

django-bird provides a custom staticfiles finder to serve component assets through Django's static files system. This allows you to collect all component assets using Django's `collectstatic` command and serve them efficiently in production.

To enable the custom finder, `BirdAssetFinder` must be in the list in your `STATICFILES_FINDERS` setting. If you aren't using the [django-bird-autoconf](https://pypi.org/project/django-bird-autoconf/) plugin, you will need to add the finder manually:

```{code-block} python
:caption: settings.py

STATICFILES_FINDERS = [
    # ... your existing finders ...
    "django_bird.staticfiles.BirdAssetFinder",
]
```

After adding the finder, run:

```bash
python manage.py collectstatic
```

This will collect all component assets into your static files directory, allowing you to serve them via your web server, [WhiteNoise](https://whitenoise.readthedocs.io), or a CDN.

## Asset Manifest

For production deployments, django-bird provides a management command to generate an asset manifest:

```bash
python manage.py generate_asset_manifest
```

This command creates a manifest file at `STATIC_ROOT/django_bird/manifest.json` that maps templates to their used components. In production mode, this manifest is used to load assets without scanning templates at runtime.

### Integration with collectstatic

For optimal deployment, follow this sequence:

1. Run `python manage.py collectstatic` first to collect all component assets
2. Then run `python manage.py generate_asset_manifest` to create the manifest file in the collected static files

This ensures that:
- All component assets are properly collected by the Django staticfiles system
- The manifest is generated with up-to-date component information
- The manifest file is placed in the correct location within your static files directory

For automated deployments, you can combine these commands:

```bash
python manage.py collectstatic --noinput && python manage.py generate_asset_manifest
```
