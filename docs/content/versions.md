---
title: Multiple versions
icon: icons/versions.svg
---

When we talk about documentation versioning, we refer to two different things:

A) One is archiving a particular version of your docs for future reference, so you never need to edit those files again.
B) The other is having two or more separate "live" versions of your documentation that you need to keep separate but want to keep updating.

Luckily, WriteADoc makes it easy to do either or both.


## A. Archiving the current version

To archive the current version of your documentation for future reference, follow these steps.

### 1. Set a current version

First, make sure you have specified a version in your site data.

```python {hl_lines="5 6"}
docs = Docs(
    __file__,
    pages=pages,
    views=views,
    site={
        "version": "1.0",
        ...
    },
)
```

### 2. Generate a snapshot

Generate a snapshot of the documentation by running:

```bash
python docs.py build --archive
```

This will build your documentation and save it into the folder `archive/{VERSION}/` (e.g., `archive/1.0/`), with all relative URLs updated to point to the files in that version.

If you haven't removed it from your view, a banner will be added to every page as well.

<figure markdown="span">
![Version banner](/assets/images/version-banner-light.png){ .only-light }
![Version banner](/assets/images/version-banner-dark.png){ .only-dark }
<figcaption>Version banner</figcaption>
</figure>


### 3. Add the version to the selector

Add a link to the list of options in the version selector at `views/layout.jinja` and rebuild your current documentation. You might need to uncomment the selector if it's your first time using it.

```html+jinja {title="views/language_popover.jinja" linenums="7"}
<div id="version-selector" popover="auto">
  <div>
    <a href="/1.0/" {% if site.version == "1.0" %}class="selected"{% endif %}>1.0</a>
    <a href="/0.5/" {% if site.version == "0.5" %}class="selected"{% endif %}>0.5</a>
  </div>
</div>
```

/// note

The version selector does not render in archived versions. Otherwise, it would link only to versions that existed when created, which might not even be available anymore.
///

### 4. Deploy

You can now copy the generated version folder along with the rest of your live documentation, so your main documentation will be at `http://example.com/`, and the documentation for the archived version will be available at `http://example.com/{VERSION}/`.

Make sure you also commit the `archive/` folder to your source code.


## B. Managing separate "live" versions

The easiest way to work with separate versions of your documentation is to have a separate instance of WriteADoc for each version and collect them in the `variants` dictionary of your main instance:

```python {hl_lines="1 11 26-27"}
docs_v1 = Docs(
    __file__,
    pages=pages_v1,
    views=views,
    site={
        "version": "1.0",
        ...
    },
)

docs_v2 = Docs(
    __file__,
    pages=pages_v2,
    views=views,
    site={
        "version": "2.0",
        ...
    },
)

docs = Docs(
    __file__,
    pages=pages,
    views=views,
    variants={
      "1.0": docs_v1,
      "2.0": docs_v2,
    }
)
```

The keys of the `variants` dictionary will be used as a **prefix** added to every URL of the generated documentation for each version. Each version will also be generated into the `build/{prefix}` folders, so your `build` folder will look like this:

```bash
build/
  ├── 1.0/
  │     ├── assets/
  │     ├── docs/
  │     └── index.html
  └── 2.0/
  │     ├── assets/
  │     ├── docs/
  │     └── index.html
  ├── assets/
  ├── docs/
  └── index.html

```

/// note

The prefixes don't need to be equal to the version numbers. They can be any string, for example:

```python
variants={
  "v1": docs_v1,
  "v2": docs_v2,
}
```