---
title: Links
icon: icons/link.svg
---

To create a link, enclose the link text in brackets (e.g., [Duck Duck Go]), and then follow it immediately with the URL in parentheses (e.g., (https://duckduckgo.com)).

/// example | Links

```md
My favorite search engine is [Duck Duck Go](https://duckduckgo.com).
```

My favorite search engine is [Duck Duck Go](https://duckduckgo.com).

///

You can optionally add a title to a link. This will appear as a tooltip when the user hovers over the link. To add a title, enclose it in quotation marks after the URL.

/// example | Links with title

```md
My favorite search engine is [Duck Duck Go](https://duckduckgo.com "The best for privacy").
```

My favorite search engine is [Duck Duck Go](https://duckduckgo.com "The best for privacy").

///


## Quick links

To quickly turn a URL or email address into a link, enclose it in angle brackets.

/// example | Quick links

```md
<https://www.markdownguide.org>

<fake@example.com>
```

<https://www.markdownguide.org>

<fake@example.com>

///

## Formatting Links

To emphasize links, add asterisks before and after the brackets and parentheses. To denote links as code, add backticks inside the brackets.

/// example | Links with format

```md
The **[EFF website](https://eff.org)**.

This is the *[Markdown Guide](https://www.markdownguide.org)*.

See the section on [`code`](#code).
```

The **[EFF website](https://eff.org)**.

This is the *[Markdown Guide](https://www.markdownguide.org)*.

See the section on [`code`](#code).

///


## Attributes

You can add extra attributes to a link, like `target="blank"`, using the [attribute lists](/attributes/) syntax.

/// example | Link with extra attributes

```md
[Opens in a new tab](https://www.python.org/){ target="blank" }
```

[Opens in a new tab](https://www.python.org/){ target="blank" }

///