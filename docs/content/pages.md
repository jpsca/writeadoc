---
title: Listing your pages
---

```python
docs = Docs(__file__, pages=[ ... ])
```

Every page you want to include in your documentation must be listed in the `pages` argument. This list can contain two things:

### A.  A path of a markdown file, relative to the `content` folder

<div markdown="1">

![Nav A](/assets/images/temp-light.png){ .only-light .right }
![Nav A](/assets/images/temp-dark.png){ .only-dark .right }

```python
docs = Docs(__file__, pages=[
  "overview/intro.md",
  "markdown/lists/tasks.md",
])
```

</div>

The title shown will be extracted from the page metadata `title`.

The folder structure of these files doesn't matter; they will all appear at the same level.
If you want to display them inside a "folder," put them inside a section.


### B. A section that can contain more pages or subsections

<div markdown="1">

![Nav C](/assets/images/temp-light.png){ .only-light .right }
![Nav C](/assets/images/temp-dark.png){ .only-dark .right }

```python
docs = Docs(__file__, pages=[
  {
    "title": "Markdown",
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

The other thing the `pages` list can contain is a section definition.
This must have a `title` and their own list of pages.

The `pages` list of the section can contain pages as paths, or other subsections.
