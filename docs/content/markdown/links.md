---
title: Links
icon: icons/link.svg
---

To create a link, enclose the link text in brackets (e.g., [Duck Duck Go]), and then follow it immediately with the URL in parentheses (e.g., (https://duckduckgo.com)).

::: div example
```md
My favorite search engine is [Duck Duck Go](https://duckduckgo.com).
```

My favorite search engine is [Duck Duck Go](https://duckduckgo.com).
:::

You can optionally add a title to a link. This will appear as a tooltip when the user hovers over the link. To add a title, enclose it in quotation marks after the URL.

::: div example
```md
My favorite search engine is [Duck Duck Go](https://duckduckgo.com "The best for privacy").
```

My favorite search engine is [Duck Duck Go](https://duckduckgo.com "The best for privacy").
:::


## Quick links

To quickly turn a URL or email address into a link, enclose it in angle brackets.

::: div example
```md
<https://www.markdownguide.org>

<fake@example.com>
```

<https://www.markdownguide.org>

<fake@example.com>
:::

## Formatting Links

To emphasize links, add asterisks before and after the brackets and parentheses. To denote links as code, add backticks inside the brackets.

::: div example
```md
The **[EFF website](https://eff.org)**.

This is the *[Markdown Guide](https://www.markdownguide.org)*.

See the section on [`code`](#code).
```

The **[EFF website](https://eff.org)**.

This is the *[Markdown Guide](https://www.markdownguide.org)*.

See the section on [`code`](#code){id="code"}.
:::


## Attributes

You can add extra attributes to a link, like `target="blank"`, using the [attribute lists](/docs/markdown/attributes/) syntax.

::: div example
```md
[Opens in a new tab](https://www.python.org/){target="_blank"}
```

[Opens in a new tab](https://www.python.org/){target="_blank"}
:::