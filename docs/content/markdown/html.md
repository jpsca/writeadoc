---
title: HTML
icon: icons/html.svg
---

Markdown is a subset of HTML; anything that cannot be expressed in Markdown can always be expressed directly with raw HTML. HTML is much less readable than plain Markdown, so you should only use it as a last resort.

The content inside HTML tags is treated differently depending if the HTML tags are inline or blocks.

## Inline syntax

Only inline syntax, such as links, strong, emphasis, etc., is rendered as regular Markdown code. For example:

```md
So <span class="special">**many** _books_</span>. So little time.
```

renders as:

```html
<p>So <span class="special"><strong>>many<strong>
  <em>books</em></span>. So little time.<p>
```

## Block syntax

For any block-level element everything inside that element is ignored, including child elements. For example:

```md
<div>
# *Not* a header
</div>
```

renders as:

```html
<div>
# <em>Not</em> a header
</div>
```

Use blank lines to separate block-level HTML elements, like `<div>`, `<table>`, `<p>`, etc., from the surrounding content.

### Indentation

Block-level HTML elements must have no indentation at all. Unless they are inside a list elementy, in which case must be indented only the same as the list text.

```md
<p class="a">Not indented</p>

- lorem
- ipsum
  <p class="b">barely indented</p>
- sit amet
```

renders (approximately) as:

```html
<p class="a">Not indented</p>
<ul>
  <li>lorem</li>
  <li>ipsum
    <p class="b">barely indented</p>
  </li>
  <li>sit amet</li>
</ul>
```
