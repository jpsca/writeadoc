---
title: Admonitions
icon: icons/admonition.svg
---

Admonitions, also known as _call-outs_, are an excellent choice for including
side content without significantly interrupting the document flow:

/// note | Some title
Hi, this is an admonition box.
///

## Syntax

Admonitions are created using the following syntax:

```md
/// admonition | Some title
    type: classname

Some content
///
```

`type` will be used as the CSS class name and as the default title. It must be a
single word. For instance:

```md
/// admonition
    type: note

Some content.

More content.
///
```

will render as:

/// admonition
    type: note

Some content.

More content.
///

Optionally, you can use custom titles. For example:

```md
/// admonition | Don't try this at home
    type: error

This is an admonition box
///
```

will render as:

/// admonition | Don't try this at home
    type: error

This is an admonition box
///

If you don't want a title, leave it blank:

```md
/// admonition |
    type: error

This is an admonition box without a title. It's not very fancy, is it?
///
```

results in:

/// admonition |
    type: error

This is an admonition box without a title. It's not very fancy, is it?
///

## Supported types

As a shortcut, there are a number of admonition blocks that can be used directly, like this:

```md
/// note
This is a note
///
```

WriteADoc includes these default types: `note`, `tip`, `warning`, `error`, `new`, `example`, and `question`.

/// note
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

<!-- -->

/// tip
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

<!-- -->

/// warning
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

<!-- -->

/// error
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

<!-- -->

/// new
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

<!-- -->

/// example
In this type of admonition, the font size is slightly larger.
///

<!-- -->

/// question
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
///

## Collapsible admonitions (details)

If instead of `admonition` you use `details`, the admonition is rendered as a
details/summary block with a small toggle on the right side:

```md
/// details | Some summary
    type: warning

Some content
///
```

will render as:

/// details | Some summary
    type: warning

Some content
///

If you wish to specify a details block as open (not collapsed), simply use the `open` option.

```md
/// details | Some summary
    open: True

Some content
///
```

will render as:

/// details | Some summary
    open: True

Some content
///

Collapsible admonitions have the same predefined types as regular admonitions
(`note`, `tip`, `warning`, `error`, `new`, `example`, and `question`), but unlike admonitions,
details do not register any shortcut syntax by default.

This feature uses the [`pymdownx.blocks.details`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/details/)
extension, and can be configured in the markdown options.

## Inline admonitions

If the screen is wide enough, you can have inline admonitions, aligned to the left or right, by wrapping the content
in a `<div markdown="1"></div>` tag and adding the "left" or "right" class to the admonition.
Leave a blank line before and after the admonition.

/// example | Admonition, aligned to the left (if your screen width >= 960px)

/// tip | Lorem Ipsum
    attrs: { class: left }

Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
///

```md
<div markdown="1">

/// tip | Lorem Ipsum
    attrs: { class: left }

Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
///

Some other content

</div>
```

///

<!--  -->

/// example | Admonition, aligned to the right (if your screen width >= 960px)

/// tip | Lorem Ipsum
    attrs: { class: right }

Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
///

```md
<div markdown="1">

/// tip | Lorem Ipsum
    attrs: { class: right }

Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
///

Some other content

</div>
```

///
