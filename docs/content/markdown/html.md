---
title: HTML
icon: icons/html.svg
---

Markdown is a subset of HTML; anything that cannot be expressed in Markdown can always be expressed directly with raw HTML.
HTML is much less readable than plain Markdown, so you should only use it as a last resort.

Use blank lines to separate block-level HTML elements, like `<div>`, `<table>`, `<p>`, etc., from the surrounding content.

## Markdown in HTML

By default, Markdown ignores any content within a raw HTML block-level element. However, you can enable parsing of the content inside a raw HTML block-level element as Markdown by including a `markdown` attribute on the opening tag. The markdown attribute will be stripped from the output, while all other attributes will be preserved.

The markdown attribute can be assigned one of three values: "1", "block", or "span".

### `markdown="1"`

When the markdown attribute is set to "1", the parser will use the default behavior for that specific tag.

The following tags have block behavior by default: `article`, `aside`, `blockquote`, `body`, `colgroup`, `details`, `div`, `dl`, `fieldset`, `figcaption`, `figure`, `footer`, `form`, `group`, `header`, `hgroup`, `hr`, `iframe`, `main`, `map`, `menu`, `nav`, `noscript`, `object`, `ol`, `output`, `progress`, `section`, `table`, `tbody`, `tfoot`, `thead`, `tr`, `ul`, and `video`.

/// example | Default "block" markdown parsing

```md
<div markdown="1">
This is a *Markdown* Paragraph.
</div>
```

renders as:

```html
<div>
<p>This is a <em>Markdown</em> Paragraph.</p>
</div>
```

///

The following tags have span behavior by default: `address`, `dd`, `dt`, `h[1-6]`, `legend`, `li`, `p`, `td`, and `th`.

/// example | Default "span" markdown parsing

```md
<p markdown="1">
This is not a *Markdown* Paragraph.
</p>
```

renders as:

```html
<p>
This is not a <em>Markdown</em> Paragraph.
</p>
```

///

Note how an implicit paragraph was added in the first example but not in the second.

### `markdown="block"`

When the markdown attribute is set to "block", the parser will force block behavior on the contents of the element, as long as it is one of the block or span tags.

The content of a block element is parsed into block-level content. In other words, the text is rendered as paragraphs, headers, lists, blockquotes, etc. Any inline syntax within those elements is processed as well.

/// example | Forced "block" markdown parsing

```md
<section markdown="block">
# A header.

A *Markdown* paragraph.

* A list item.
* A second list item.

</section>
```

renders as:

```html
<section>
<h1>A header.</h1>
<p>A <em>Markdown</em> paragraph.</p>
<ul>
<li>A list item.</li>
<li>A second list item.</li>
</ul>
</section>
```

///

<!--  -->

/// warning
Forcing elements to be parsed as `block` elements when they are not by default could result in invalid HTML.

For example, one could force a `<p>` element to be nested within another `<p>` element. In most cases, it is
recommended to use the default behavior of `markdown="1"`.
///


### `markdown="span"`

When the markdown attribute is set to "span", the parser will force span behavior on the contents of the element, as long as it is one of the block or span tags.

The content of a span element is not parsed into block-level content. In other words, the content will not be rendered as paragraphs, headers, etc. Only inline syntax will be rendered, such as links, strong, emphasis, etc.

/// example | Forced "span" markdown parsing

```md
<div markdown="span">
# *Not* a header
</div>
```

renders as:

```html
<div>
# <em>Not</em> a header
</div>
```

///


## Nesting

When nesting multiple levels of raw HTML elements, a markdown attribute must be defined for each block-level element. For any block-level element that does not have a markdown attribute, everything inside that element is ignored, including child elements with markdown attributes.

/// example | Markdown in nested HTML

```md
<article id="my-article" markdown="1">
# Article Title

A Markdown paragraph.

<section id="section-1" markdown="1">
## Section 1 Title

<p>Custom raw **HTML** which gets ignored.</p>

</section>

<section id="section-2" markdown="1">
## Section 2 Title

<p markdown="1">**Markdown** content.</p>

</section>

</article>
```

renders as:

```html
<article id="my-article">
<h1>Article Title</h1>
<p>A Markdown paragraph.</p>
<section id="section-1">
<h2>Section 1 Title</h2>
<p>Custom raw **HTML** which gets ignored.</p>
</section>
<section id="section-2">
<h2>Section 2 Title</h2>
<p><strong>Markdown</strong> content.</p>
</section>
</article>
```
