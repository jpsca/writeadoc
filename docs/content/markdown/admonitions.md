---
title: Admonitions
icon: icons/admonition.svg
---

Admonitions, also known as _call-outs_, are an excellent choice for including
side content without significantly interrupting the document flow:

::: note | Some title
Hi, this is an admonition box.
:::

## Syntax

Admonitions are created using the following syntax:

```md
::: type | Some optional title
Some content
:::
```

`type` will be used as the CSS class name and as the default title. It must be a
single word. For instance:

```md
::: note
Some content.

More content.
:::
```

will render as:

::: note
Some content.

More content.
:::

Optionally, you can use custom titles. For example:

```md
::: error | Don't try this at home
This is an admonition box
:::
```

will render as:

::: error | Don't try this at home
This is an admonition box
:::

## Supported types

WriteADoc includes these default types: `note`, `tip`, `warning`, `error`, and `new`.

::: note
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
:::

::: tip
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
:::

::: warning
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
:::

::: error
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
:::

::: new
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et
euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
purus auctor massa, nec semper lorem quam in massa.
:::

## Collapsible admonitions (details)

If you add an `open` option, the admonition is rendered as a
details/summary block with a small toggle on the right side:

```md
::: note | Some summary
:open: false

Some content
:::
```

will render as:

::: note | Some summary
:open: false

Some content
:::

If you wish to specify a details block as open (not collapsed), simply use the `:open: true` option.

```md
::: note | Some summary
:open: true

Some content
:::
```

will render as:

::: note | Some summary
:open: true

Some content
:::

## Inline admonitions

If the screen is wide enough, you can have inline admonitions, by wrapping the content
in a `:::: div columns` block (use *four* or more ":"):

:::::: div columns

::: tip | Lorem Ipsum
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
:::

```md
::::: div columns

::: tip | Lorem Ipsum
Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Nulla et euismod nulla.
:::

Some other content
:::::
```

::::::
