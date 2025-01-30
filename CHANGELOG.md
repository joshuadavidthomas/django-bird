# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [${version}]
### Added - for new features
### Changed - for changes in existing functionality
### Deprecated - for soon-to-be removed features
### Removed - for now removed features
### Fixed - for any bug fixes
### Security - in case of vulnerabilities
[${version}]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v${version}
-->

## [Unreleased]

## [0.13.0]

🚨 This release contains some breaking changes. See the Deprecated and Removed sections for more information. 🚨

### Added

- Added `BirdAssetFinder`, a custom staticfiles finder to serve component assets through Django's staticfiles app.
- Added automatic configuration of `STATICFILES_FINDERS` to include `BirdAssetFinder` when `ENABLE_AUTO_CONFIG=True`.
- Added support for Django 5.2.

### Changed

- **Internal**: Renamed `TemplateConfigurator` to `AutoConfigurator` and consolidated configuration logic.
- **Internal**: Refactored component and asset loading strategy to track relationships between templates and components, affecting `ComponentRegistry.discover_components` and the `{% bird:asset %}` templatetag.

### Deprecated

- The built-in asset serving view (`asset_view`) is deprecated and will be removed in the next minor version (v0.14.0). Use `BirdAssetFinder` with Django's staticfiles app.
- The `BirdLoader` template loader is deprecated and will be removed in a future version. If you have enabled manual configuration by setting `ENABLE_AUTO_CONFIG=False`, please remove `django_bird.loader.BirdLoader` from your `TEMPLATES` setting.

### Removed

- Removed the deprecated `ENABLE_BIRD_ID_ATTR` setting.
- Removed automatically discovering templates in `BASE_DIR/templates`. Templates must now be in directories configured in Django's template engine settings or app template directories.
- Removed component scanning functionality from `BirdLoader`.
- Removed `django_bird.compiler.Compiler`.

### Fixed

- Fixed asset loading in `{% bird:asset %}` templatetags to only render assets from components actually used in the current template by tracking template-component relationships during component discovery.

## [0.12.1]

### Changed

- **Internal**: Refactored slot handling logic by moving slot processing from `BirdNode` to `BoundComponent`.
- **Internal**: Simplified component context management in `BirdNode` by offloading context prep to `BoundComponent`.
- **Internal**: Refactored prop rendering in `Params` to take a `Component` instance instead of the raw `NodeList`.

### Removed

- **Internal**: Removed standalone `Slots` dataclass abstraction in favor of handling in `BoundComponent`.

### Fixed

- Fixed default slot content handling when using `only` keyword for component context isolation.

## [0.12.0]

### Added

- Added `data-bird-<component_name>` data attribute to the `attrs` template context variable for components when `ENABLE_BIRD_ATTRS` is enabled.

### Changed

- **Internal**: Refactored component rendering by introducing a new `BoundComponent` class and moving some of the rendering logic from `Component` and `BirdNode` to this new class.
- Renamed `ENABLE_BIRD_ID_ATTR` setting to `ENABLE_BIRD_ATTRS` to reflect its expanded functionality.
- Moved setting the `data-bird-id` data attribute in the `attrs` template context variable to `BoundComponent` and added a sequence number to better uniquely identify multiple instances of the same component.

### Deprecated

- The `ENABLE_BIRD_ID_ATTR` setting is deprecated and will be removed in the next minor version (v0.13.0). Use `ENABLE_BIRD_ATTRS` instead.

### Removed

- **Internal**: Removed `Component.render` method in favor of new `BoundComponent.render` method.

## [0.11.2]

### Changed

- Improved component context handling by using `Context` objects directly when a component uses the outside template context, instead of flattening the context `dict`.
- **Internal**: Renamed `only` argument for `BirdNode` to `isolated_context`. This doesn't affect the public API of passing `only` to the template tag.
- Standardized component names to use dots instead of slashes for nested paths (e.g., "nested.button" instead of "nested/button").

## [0.11.1]

### Changed

- **Internal**: Changed component ID generation to use MD5 hash of name, path, and normalized source instead of Python's built-in hash function. This provides more consistent IDs across different Python processes.

## [0.11.0]

### Added

- Added `ENABLE_BIRD_ID_ATTR` setting (default: `True`) to control whether components receive an automatic `data-bird-id` attribute. This is to help with component identification in the DOM and for a future planned feature around JS/CSS asset scoping.

## [0.10.3]

### Fixed

- Fixed the potential for duplicate asset tags in the `{% bird:css %}` and `{% bird:js %}` templatetags by using a `set` instead of a `list` when collecting a template's component assets.

### Changed

- **Internal**: Refactored asset rendering logic by centralizing tag name parsing and HTML tag generation to the `django_bird.staticfiles` module.

## [0.10.2]

### Changed

- Changed asset URLs to use django-bird's asset view instead of file paths.

## [0.10.1]

### Fixed

- Fixed asset serving view to properly stream files using `FileResponse` instead of reading file contents directly.

## [0.10.0]

### Added

- Added built-in view and URLs for serving component assets in development. Note: This is not recommended for production use.

## [0.9.2]

### Changed

- Changed component name handling to preserve quotes, allowing literal string names to bypass dynamic resolution (e.g. `{% bird "button" %}` will always use "button" even if `button` exists in the context).

## [0.9.1]

### Fixed

- Fixed attribute name handling in components to properly convert underscores to hyphens (e.g. `hx_get` becomes `hx-get`) for better HTML compatibility.

## [0.9.0]

### Added

- Added `only` keyword to `{% bird %}` tag for isolating component context that, when used, components cannot access their parent template's context, e.g., `{% bird button only %}`.

### Changed

- Changed handling of self-closing indicator (`/`) in `{% bird %}` tag to always treat it as a syntax marker rather adding to the component's template context.

## [0.8.2]

### Fixed

- **Internal**: Fixed component caching behavior to properly track assets. Components are now always cached for asset tracking, while still providing fresh templates in `DEBUG` mode.

## [0.8.1]

### Fixed

- Fixed component discovery for nested directories and Django app templates.

## [0.8.0]

### Changed

- **Internal**: Consolidated Component and Asset registries into a single `ComponentRegistry`.
- **Internal**: Added component discovery at app startup instead of on-demand in the template loader.

### Fixed

- Fixed default content not being rendered in slots when no content is provided.

## [0.7.2]

### Changed

- **Internal**: Improved handling of component parameters in loops by creating fresh `Params` instances for each render. Previously, a single `Params` instance was reused across renders, which could cause issues with attribute resolution in loops. The `BirdNode` now stores raw attributes instead of a `Params` instance, and creates a new `Params` instance for each render.

### Fixed

- Fixed an issue where nested variable resolution (e.g., `item.url`) would fail in loops after the first iteration. This was caused by attributes being consumed during the first render and not being available for subsequent renders.

## [0.7.1]

### Removed

- **Internal**: Removed debug prints from `BirdNode` template tag node.

## [0.7.0]

### Changed

- Improved handling of quoted vs unquoted attribute values in `{% bird %}` components. Quoted values (e.g., `class="static-class"`) are treated as literal strings, while unquoted values (e.g., `class=dynamic_class`) are resolved from the template context. This allows for more explicit control over whether an attribute value should be treated as a literal or resolved dynamically.

### Fixed

- **Internal**: Simplified asset management by using a global registry, making it work reliably with any template loader configuration.

## [0.6.2]

### Changed

- When `DEBUG=True`, the `django_bird.components.Registry` will no longer cache the retrieval of `Component` instances.

## [0.6.1]

### Fixed

- Fixed a `TypeError` in the `BirdLoader` when scanning for assets if a `Template` or `Node` had a `None` nodelist. This could occur with self-closing `{% bird component / %}` components and their corresponding `BirdNode` instances.

## [0.6.0]

### Added

- New `{% bird:css %}` and `{% bird:js %}` template tags to automatically include component assets
- Component assets are automatically discovered from matching CSS/JS files next to component templates

### Changed

- **Internal**: Extended `BirdLoader` to track component usage and their assets during template rendering
- **Internal**: Assets are now stored as frozensets for immutability
- **Internal**: Added `ComponentAssetRegistry` to manage component assets during template rendering
- **Internal**: Refactored `AssetType` to use string values and file extensions

### Removed

- **Internal**: Simplified asset handling by removing global registry in favor of per-component assets

## [0.5.0]

### Added

- Added component caching with LRU (Least Recently Used) strategy via global `components` registry.
    - `cachetools>=5.5.0` is now a dependency of the library to support this new cache strategy

### Changed

- **Internal**: Flattened package structure by moving files from `components/` subdirectory to root level. No public API changes.
- **Internal**: `BirdNode` now uses cached components instead of creating new ones each time.

## [0.4.0]

### Changed

- Improved handling of boolean attributes to support all forms of Django template syntax and string values. The attribute name alone (`disabled`), explicit booleans (`disabled=True`), or string values (`disabled="True"`) all work as expected - rendering just the attribute name when true and omitting it when false.

## [0.3.0]

### Added

- Created `{% bird:prop %}` tag for defining properties within components. These operate similarly to the `{{ attrs }}` template context variable, but allow for setting defaults. Any attributes passed to a component will override the prop's default value, and props defined in a component template are automatically removed from the component's `attrs`. Props are accessible in templates via the `props` context variable (e.g. `{{ props.id }}`)

## [0.2.0]

🚨 This release contains a breaking change. See the Changed section for more information. 🚨

### Added

- Added support for dynamic component names in `{% bird %}` tag. Component names can now be variables, e.g. `{% bird component_type %}` where `component_type` is a variable in the template context.

### Changed

- Reversed template resolution order to prefer component-specific templates over generic ones.

  For example, given a component named `button`, the previous resolution order was:

  1. `button.html`
  2. `button/button.html`
  3. `button/index.html`

  The new resolution order is:

  1. `button/button.html`
  2. `button/index.html`
  3. `button.html`

## [0.1.1]

### Fixed

- Fixed rendering of flat attributes in `{% bird %}` component templates. Previously, a small mistake in trying to render `boolean` values caused no attributes to be rendered. E.g. `{% bird foo disabled=True %}` should have been rendered using `{{ attrs }}` inside the `foo` bird component as just `disabled` -- instead nothing was being rendered, even `key="value"` attributes.

## [0.1.0]

### Added

- Created `{% bird %}` tag for creating reusable components in Django templates.
- Created `{% bird:slot %}` tag for defining and using named slots within components.
- Included a custom template compiler for compilation and caching of Bird components. This is essentially a no-op for now and just there as a stub for future changes.
- Created a custom template loader for integration with django-bird's compiler and Django's template engine.
- Added support for nested components and dynamic slot rendering.
- Initial configuration of the library through the `settings.DJANGO_BIRD` dictionary, including these settings:
    - `COMPONENT_DIRS` - List of directories to search for components
    - `ENABLE_AUTO_CONFIG` - Boolean to enable/disable auto-configuration

### New Contributors

- Josh Thomas <josh@joshthomas.dev> (maintainer)

[unreleased]: https://github.com/joshuadavidthomas/django-bird/compare/v0.13.0...HEAD
[0.1.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.1.0
[0.1.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.1.1
[0.2.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.2.0
[0.3.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.3.0
[0.4.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.4.0
[0.5.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.5.0
[0.6.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.6.0
[0.6.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.6.1
[0.6.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.6.2
[0.7.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.7.0
[0.7.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.7.1
[0.7.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.7.2
[0.8.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.8.0
[0.8.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.8.1
[0.8.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.8.2
[0.9.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.9.0
[0.9.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.9.1
[0.9.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.9.2
[0.10.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.10.0
[0.10.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.10.1
[0.10.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.10.2
[0.10.3]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.10.3
[0.11.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.11.0
[0.11.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.11.1
[0.11.2]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.11.2
[0.12.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.12.0
[0.12.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.12.1
[0.13.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.13.0
