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

[unreleased]: https://github.com/joshuadavidthomas/django-bird/compare/v0.2.0...HEAD
[0.1.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.1.0
[0.1.1]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.1.1
[0.2.0]: https://github.com/joshuadavidthomas/django-bird/releases/tag/v0.2.0
