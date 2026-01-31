---
title: Write
---

Success! You are now ready to start writing.

The main content of your page is written in Markdown.
WriteADoc transforms your Markdown into HTML code and uses the `views/page.jinja` view to generate the final HTML file.
It also does other things, like extracting the page metadata and processing the text to build a searchable index.

It uses common Markdown syntax with many popular extensions. You can read about all the supported syntax in the [Markdown section](/docs/markdown).


## Setting the page title and other metadata

Each page must have a metadata section at the beginning. This is a list of `name: value` pairs
that many tools call "Frontmatter".

```{tip} Actually...
The metadata is parsed as a [restricted subset of the YAML format](https://hitchdev.com/strictyaml/)
and can also contain lists and multi-line strings.
```

To set it, add a section surrounded by `---` at the beginning of each of your pages, like this:

```md {hl_lines="1-3"}
---
title: Lorem ipsum
---

Dolor sit amet
```

You must at least set a title, which is used in the navigation sidebar, search, and other places.

You don't need to repeat the title as a header.


### Description

You can optionally set a page description. This will be used in the HTML metadata for the page.
If you don't set one, the site description will be used instead.

```md {hl_lines="3"}
---
title: Lorem ipsum
description: Latin is actually cool
---
```

### Icon

Adding an icon is optional. If you use one, it will be shown in the documentation index.
An icon should be a path, relative to the "assets" folder, of a small image or an SVG file.


```md {hl_lines="3"}
---
title: Lorem ipsum
icon: images/icon.svg
---
```

----

This is the minimal metadata a page should have, but you can freely add others and use them in your custom views.

