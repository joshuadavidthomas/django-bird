# Organizing Components

As components grow in complexity, effective organization becomes crucial. Let's explore approaches, starting from a basic implementation to more sophisticated structures.

Let's start with a simple icon component and evolve its organization. We'll create a component using the [Heroicons](https://heroicons.com) library.

```{note}
This is for demonstration purposes. For real-world applications using Heroicons, consider using Adam Johnson's [heroicon](https://github.com/adamchainz/heroicons) Python package.
```

## Basic Approach: Single File

Let's start by including all component variations in a single file:

```{code-block} htmldjango
:caption: templates/bird/icon.html

{% bird:prop name %}

{% if props.name == "arrow-down" %}
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5 12 21m0 0-7.5-7.5M12 21V3" />
    </svg>
{% elif props.name == "arrow-left" %}
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
    </svg>
{% elif props.name == "arrow-right" %}
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
    </svg>
{% elif props.name == "arrow-up" %}
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
    </svg>
{% endif %}
```

In this example, the icon variant is a passed-in [attribute](attrs.md). Using this component looks like this:

```htmldjango
{% bird icon name="arrow-down" / %}
```

```{tip}
The / at the end of the component definition means it’s a self-closing component. You don’t need a `{% endbird %}` closing tag and can use it for components that don't need to provide any [slots](slots.md) for content.
```

This approach is simple and works for smaller components, but can quickly lead to an unwieldy file as the number of variations increases. Additionally, this does not allow composing different components together.

## Alternative Approaches

Let's explore scalable ways to organize and structure components.

1. **Flat Structure**

    Split components into separate files in the same directory. This approach is simple to implement and navigate for a moderate number of components.

    ```bash
    templates/bird/
    ├── icon.arrow-down.html
    ├── icon.arrow-left.html
    ├── icon.arrow-right.html
    └── icon.arrow-up.html
    ```

    Bird components take the component name from the filename. Using components this way changes the syntax slightly:

    ```htmldjango
    {% bird icon.arrow-down / %}
    ```

2. **Dedicated Directories**

    ```bash
    templates/bird/
    └── icon/
        ├── arrow-down.html
        ├── arrow-left.html
        ├── arrow-right.html
        └── arrow-up.html
    ```

    This allows better organization as the component count grows, making it easier to locate related components.

    django-bird converts the directory divider into a `.`, so our usage remains unchanged from the flat structure:

    ```htmldjango
    {% bird icon.arrow-down / %}
    ```

3. **Deeply Nested Directory Structure**

    You can nest the components as deep as required for more granular organization.

    ```bash
    templates/bird/
    └── icon/
        └── arrow/
            ├── down.html
            ├── left.html
            ├── right.html
            └── up.html
    ```

    This structure allows for specific categorization, which is useful for large projects with many related component variations.

    Converting the directory structure to component names would change our usage:

    ```htmldjango
    {% bird icon.arrow.down / %}
    ```

## Real-World Example: Accordion

Let's examine a complex, real-world example: an accordion component. This component consists of multiple nested parts, demonstrating how our organizational approaches apply to sophisticated structures.

Here's an example of using our accordion component, based on an MDN [example](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details#multiple_named_disclosure_boxes_):

```htmldjango
{% bird accordion %}
    {% bird accordion.item name="reqs" %}
        {% bird accordion.heading %}
            Graduation Requirements
        {% endbird %}
        {% bird accordion.content %}
            Requires 40 credits, including a passing grade in health, geography,
            history, economics, and wood shop.
        {% endbird %}
    {% endbird %}

    {% bird accordion.item name="reqs" %}
        {% bird accordion.heading %}
            System Requirements
        {% endbird %}
        {% bird accordion.content %}
            Requires a computer running an operating system. The computer must have some
            memory and ideally some kind of long-term storage. An input device as well
            as some form of output device is recommended.
        {% endbird %}
    {% endbird %}

    {% bird accordion.item name="reqs" %}
        {% bird accordion.heading %}
            Job Requirements
        {% endbird %}
        {% bird accordion.content %}
            Requires knowledge of HTML, CSS, JavaScript, accessibility, web performance,
            privacy, security, and internationalization, as well as a dislike of
            broccoli.
        {% endbird %}
    {% endbird %}
{% endbird %}
```

Here's how these components might be implemented internally:

```{code-block} htmldjango
:caption: `accordion`
<div>
    {{ slot }}
</div>
```

```{code-block} htmldjango
:caption: `accordion.item`
<details {{ attrs }}>
    {{ slot }}
</details>
```

```{code-block} htmldjango
:caption: `accordion.heading`
<summary>
    {{ slot }}
</summary>
```

```{code-block} htmldjango
:caption: `accordion.content`
<p>
    {{ slot }}
</p>
```

These internal implementations show the accordion’s structure, with slots for content.

Let's explore different ways to organize the accordion component files:

1. In the base of the bird components directory:

    ```bash
    templates/bird/
    ├── accordion.html
    ├── accordion.heading.html
    ├── accordion.item.html
    └── accordion.content.html
    ```

    This approach keeps all accordion-related components in the same directory as other components.

2. With a dedicated accordion directory:

    ```bash
    templates/bird/
    └── accordion/
        ├── accordion.html
        ├── heading.html
        ├── item.html
        └── content.html
    ```

    We group all accordion components in a dedicated directory.

    When using `{% bird accordion %}`, the library will look for components in the following order:

    1. `accordion/accordion.html`
    2. `accordion/index.html`
    3. `accordion.html`

    This search order allows for more organizational flexibility.

    For example, you can structure your files like this:

    ```bash
    templates/bird/
    └── accordion/
        ├── heading.html
        ├── index.html  # primary accordion component
        ├── item.html
        └── content.html
    ```

    Or like this:

    ```bash
    templates/bird/
    ├── accordion
    │   ├── heading.html
    │   ├── item.html
    │   └── content.html
    └── accordion.html
    ```

    This flexibility in naming and organization allows you to use `accordion.html` for explicit naming, `index.html` as a generic entry point, or use a flat structure if neither exists in the accordion directory.

    The component usage in your templates remains the same, regardless of the structure. This approach provides options for organizing components based on project needs and team preferences while maintaining consistent usage patterns.

## Choosing the Right Approach

Each organizational method offers different trade-offs between simplicity and structure.

The choice depends on various factors:

- Project size and complexity
- Team size and preferences
- Future scalability needs
- Maintenance ease

These approaches aren't mutually exclusive. Larger projects might benefit from using a combination of these methods, applying different structures to different parts of the application as needed.

As your project evolves, you may benefit from refactoring your component organization. Starting with a simpler structure and moving to more complex ones as needed helps maintain clarity and scalability throughout your project's lifecycle.
