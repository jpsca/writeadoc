---
title: Configuration
---

WriteADoc has a unique take on configuration: the documentation is managed by a python `Docs` class that you import, intantiate with your data,
and then render by calling a method, All of this happens inside your `docs.py` file.

```python {title="docs.py"}
from writeadoc import Docs

pages = [
    "welcome.md",
    # ...
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "Project Name",
        "description": "Description of your project",
        "base_url": "https://project.example.com",
        "lang": "en",
        "version": "1.0",
        "source_code": "https://github.com/yourusername/yourproject/",
    },
)

if __name__ == "__main__":
    docs.cli()

```

The main arguments are the list of pages and the site metadata.


## Adding pages

Every page you want to include in your documentation must be listed in the `pages` argument.

```python {title="docs.py" hl_lines="3"}
docs = Docs(
  __file__,
  pages=[ ... ],
  site={ ... }
)
```

///warning
Every page **except** your `index.md` file.
///

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
It should be a path, relative to the assets folder, of an image or a svg file.

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

The `icon` is optional. If included, it should be a path, relative to the assets folder, of an image or a svg file.

The `pages` list of the section can contain page paths or other sections.

Clicking on the section title will fold/unfold their pages tree.

### Section/pages

A section can also be a page. To do this, add a `path` attribute with the path of the markdown
file, relative to the `content` folder.

You can still define a `title`, but it is optional, because it will be extracted from the page metadata.
If there is an `icon` in the page metadata -- a path, relative to the assets folder, of an image or a svg file -- it will also be shown.

<div markdown="1">

![Nav C](/assets/images/nav-sectionpage-light.png){ .only-light .right }
![Nav C](/assets/images/nav-sectionpage-dark.png){ .only-dark .right }

```python {hl_lines="4"}
docs = Docs(__file__, pages=[
  {
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

</div>

Clicking on the section title will show its page.


## Site metadata

Site metadata contains the essential global metadata: `name`, `base_url`, `version`, and `lang`.
But also any other custom metadata you might want to use in your views.

For example, `description` and `source_code` are two pieces of information that are used in several places
in the default theme.


```python {title="docs.py" hl_lines="4-11"}
docs = Docs(
  __file__,
  pages=[ ... ],
  site={
      "name": "Project Name",                     # required
      "base_url": "https://project.example.com",  # required
      "version": "1.0",                           # required
      "lang": "en",                               # required
      "description": "Description of your project",
      "source_code": "https://github.com/yourusername/yourproject/",
  },
)
```


## The Home page

The home page is special for several reasons:

#. You don't include this file in your `pages` list.
#. This file **must** be named `index.md` and be directly inside the `content` folder, not in a subfolder.
#. Unlike other pages, that use the `views/page.jinja` view, the home page uses the `views/index.jinja` view.
#. You don't even *need* an `index.md` file! If you delete it, the `views/index.jinja` view will be rendered as-is.
