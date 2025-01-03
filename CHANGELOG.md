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

[unreleased]: https://github.com/joshuadavidthomas/django-bird/compare/v0.8.1...HEAD
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
