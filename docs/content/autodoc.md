---
title: Autodoc
icon: icons/sparkles.svg
---

WriteADoc provides functionality for automatically generating documentation from Python code docstrings. It extracts information from docstrings—including descriptions, parameters, return values, examples, and more—and structures them into a standardized format.

## Usage

```md
::: api my_library.my_module.my_class_or_function
:::
```

This works with classes, functions, and individual class methods and properties.

## Example: Class

```md
::: api jx.Catalog
:::
```

::: div example
_Example of an autodoc for a class_
![Autodoc class](/assets/images/autodoc-class-light.png){ .only-light }
![Autodoc class](/assets/images/autodoc-class-dark.png){ .only-dark }
:::

----

## Example: Function

```md
::: api jx.meta.extract_metadata
:::
```

::: div example
_Example of an autodoc for a function_
![Autodoc function](/assets/images/autodoc-function-light.png){ .only-light }
![Autodoc function](/assets/images/autodoc-function-dark.png){ .only-dark }
:::

----


## Options

### Customizing What Is Documented

By default, all members of a class whose names don't start with an underscore ("_") will be included. You can include one or more members that start with an underscore using the `include` option:

```md
::: api jx.Catalog
:include: __call__ __html__
:::
```

You can also exclude some members with the `exclude` option:

```md
::: api jx.Catalog
:exclude: get_data to_dict
:include: __call__
:::
```

::: note
As you can see, the options must be separated from each other by spaces.
:::

### Showing only the class signature

To exclude **all** members (methods, propeties, etc.) of a class, use:

```md
::: api jx.Catalog
:show_members: false
:::
```

### Changing the Starting Heading Level

By default, the name of the function or class is rendered with an `<h2>`, and the names of attributes/methods with `<h3>`. You can change this by adding the starting heading level after the import path:

```md
::: api jx.meta.extract_metadata
:level: 4
:::
```

::: api jx.meta.extract_metadata
:level: 4
:::


## Notes on Docstring Parsing

The api module relies on the `docstring_parser` library to parse docstrings. It supports various docstring formats, but works best with Google-style docstrings.

For optimal results:

1. Start with a short, one-line description.
2. Follow with a blank line and then a more detailed description.
3. Use standard sections like "Arguments:" (or "Args:"), "Returns:", "Raises:", and "Examples:".
4. Document all parameters, return values, and exceptions.


## Customizing the Output

The extracted information is rendered using the `api.jinja` view, recursively. There, you can see it receives a `ds` argument with these fields:

- `name`: The name of the documented element
- `symbol`: Type of the element (e.g., "class", "function", "method")
- `label`: Additional label (e.g., "property", "attribute")
- `signature`: Function/method signature
- `params`: List of parameters (for functions/methods)
- `short_description`: First paragraph of the description
- `long_description`: Rest of the description
- `description`: The full description
- `deprecation`: Deprecation notes
- `examples`: List of examples
- `returns`: Return information
- `many_returns`: List of multiple return values
- `raises`: List of exceptions that the function may raise
- `bases`: List of base classes (for classes)
- `attrs`: List of ds objects for each attribute (for classes)
- `properties`: List of ds objects for each property (for classes)
- `methods`: List of ds objects for each method (for classes)
