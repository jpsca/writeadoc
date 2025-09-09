---
title: Listing your pages
---

Every page you want to include in your documentation must be listed in the `pages` argument.

```python {title="docs.py" hl_lines="3"}
docs = Docs(
  __file__,
  pages=[ ... ],
)
```

This list can contain three things:

### Pages

A page is specified as the path of a markdown file, relative to the `content` folder.

<div markdown="1">

![Nav A](/assets/images/nav-page-light.png){ .only-light .right }
![Nav A](/assets/images/nav-page-dark.png){ .only-dark .right }

```python
docs = Docs(__file__, pages=[
  "overview/intro.md",
  "markdown/lists/tasks.md",
])
```

</div>

The title shown will be extracted from the page metadata `title`.

If there is an `icon` in the page metadata, it will also be shown.

The folder structure of these files doesn't matter; they will all appear at the same level.
If you want to display them inside a "folder," put them inside a section.

### Sections

A section can contain more pages or subsections.

<div markdown="1">

![Nav C](/assets/images/nav-section-light.png){ .only-light .right }
![Nav C](/assets/images/nav-section-dark.png){ .only-dark .right }

```python
docs = Docs(__file__, pages=[
  {
    "title": "Lists",
    "icon": "icons/code.svg",  # optional
    "pages": [
      "markdown/lists/unordered.md",
      "markdown/lists/ordered.md",
      "markdown/lists/tasks.md",
      # ...
    ]
  },
  # ...
])
```

</div>

The `icon` is optional.

The `pages` list of the section can contain page paths or other sections.

### Section/pages

A section can also be a page. To do this, add a `path` attribute with the path of the markdown
file, relative to the `content` folder.

You can still define a `title`, but it is optional, because it will be extracted from the page metadata.

<div markdown="1">

![Nav C](/assets/images/nav-sectionpage-light.png){ .only-light .right }
![Nav C](/assets/images/nav-sectionpage-dark.png){ .only-dark .right }

```python {hl_lines="4"}
docs = Docs(__file__, pages=[
  {
    "title": "Lists",
    "path": "markdown/lists.md",
    "pages": [
      "markdown/lists/unordered.md",
      "markdown/lists/ordered.md",
      "markdown/lists/tasks.md",
      # ...
    ]
  },
  # ...
])
```
