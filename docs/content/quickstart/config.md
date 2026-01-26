---
title: Configuration
---

WriteADoc has a unique approach to configuration: documentation is managed by a Python `Docs` class that you import, instantiate with your data, and then render by calling a method. All of this happens inside your `docs.py` file.

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

```{warning}
Include every page **except** your `index.md` file.
```

A page is specified as the path of a Markdown file, relative to the `content` folder.

<!-- <div markdown="1"> -->

![Nav A](/assets/images/nav-page-light.png){ .only-light .right }
![Nav A](/assets/images/nav-page-dark.png){ .only-dark .right }
