# dj-angles Integration

If you prefer HTML-like component tags, django-bird works well with [dj-angles](https://dj-angles.adamghill.com/).

## Install

Install django-bird with the optional `angles` extra:

```bash
python -m pip install 'django-bird[angles]'
```

Or install manually:

```bash
python -m pip install django-bird dj-angles
```

## Configure Django template loaders

Add the `dj-angles` template loader before Django's filesystem/app loaders:

```python
# settings.py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "dj_angles.template_loader.Loader",
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
            "builtins": [
                "django_bird.templatetags.django_bird",
            ],
        },
    },
]
```

## Common tag styles

A few practical conventions:

- `dj-bird` + explicit template name
- `dj-` prefix for component-like tags when using the default mapper

### Explicit `dj-bird` tag

```html
<dj-bird template="button" class="btn-primary">
  Click me
</dj-bird>
```

### Default mapper (`dj-button`, `dj-modal`, etc.)

Configure `dj-angles` to map unknown tags to django-bird components:

```python
# settings.py
ANGLES = {
    "default_mapper": "dj_angles.mappers.thirdparty.map_bird",
}
```

Then use:

```html
<dj-button class="btn-primary">
  Click me
</dj-button>
```

## References

- dj-angles django-bird integration docs: <https://dj-angles.adamghill.com/en/latest/integrations/django-bird/>
- django-bird configuration docs: [configuration](configuration.md)
