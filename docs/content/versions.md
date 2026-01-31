---
title: Multiple versions
icon: icons/versions.svg
---

When we talk about documentation versioning, we refer to two different things:

A) One is archiving a particular version of your docs for future reference, so you never need to edit those files again.
B) The other is having two or more separate "live" versions of your documentation that you need to keep separate but want to keep updating.

Luckily, WriteADoc makes it easy to do either or both.


## Archiving the current version

To archive the current version of your documentation for future reference, follow these steps.

### 1. Set a current version

First, make sure you have specified a version in your site data.

```python {hl_lines="5 6"}
docs = Docs(
    __file__,
    pages=pages,
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


### 3. Enable the version selector

Go to the file `views/version_selector.jinja` and remove
the `{#` at the beginning and the `#}` at the end, so the selector appears in your documentation.

Add a link to the list of options in the version selector at `views/version_selector.jinja` and rebuild your current documentation.

```html+jinja {title="views/version_selector.jinja" hl_lines="7 8"}
<div class="version variant-popover">
    <button type="button" popovertarget="version-selector" tabindex="0">
        {{ site.version }}
    </button>
    <div class="popover" role="menu">
        <div>
            <a href="/1.0/" {% if site.version == "1.0" %}class="selected"{% endif %} tabindex="0">1.0</a>
            <a href="/0.5/" {% if site.version == "0.5" %}class="selected"{% endif %} tabindex="0">0.5</a>
        </div>
    </div>
</div>
{%- endif %}
```

![Version selector](/assets/images/version-selector-light.png){ .only-light }
![Version selector](/assets/images/version-selector-dark.png){ .only-dark }


::: note
The version selector does not render in archived versions. Otherwise, it would link only to versions that existed when created, which might not even be available anymore.
:::

### 4. Deploy

You can now copy the generated version folder along with the rest of your live documentation, so your main documentation will be at `http://example.com/`, and the documentation for the archived version will be available at `http://example.com/{VERSION}/`.

::: warning
Make sure you also commit the `archive/` folder to your source code.
:::


## Managing separate "live" versions

If you, for some reason, have to maintain live documentation for two or more versions at the same time, meaning documentation that can change, WriteADoc supports that too.

To do so, follow this procedure:

### 1. Set the default version

First, set the default version, the latest one, as before:

```python {hl_lines="5"}
docs = Docs(
    __file__,
    pages=pages,
    site={
        "version": "3.0",
        ...
    },
)
```

### 2. Create a subfolder for the content of each version

Inside the `content` folder, create a subfolder for each version. For example:

```bash
content/
  ├── 1.0/
  ├── 2.0/
  │
  └── welcome.md

```

### 3. Create instances of WriteADoc for each version

Now create a separate instance of WriteADoc for each extra version and collect them in the `variants` dictionary of your main instance:


```python {hl_lines="1 10 19 26-29"}
docs_v1 = Docs(
    __file__,
    pages=pages_v1,  # Relative to content/1.0/
    skip_home=True,
    site={
        "version": "1.0",
        ...
    },
)

docs_v2 = Docs(
    __file__,
    pages=pages_v2,  # Relative to content/2.0/
    skip_home=True,
    site={
        "version": "2.0",
        ...
    },
)

docs = Docs(
    __file__,
    pages=pages,  # Relative to content/
    site={
        "version": "3.0",
        ...
    },
    variants={
      "1.0": docs_v1,
      "2.0": docs_v2,
    },
)
```

The keys of the `variants` dictionary will be used as a **prefix** added to every URL of the generated documentation for each version.
Each version will also be generated into the `build/{prefix}` folders, so your `build` folder will look like this:

```bash
build/
  ├── 1.0/
  │    ├── docs/
  │    ├── search/
  │    └── index.html  # redirects
  |
  └── 2.0/
  │    ├── docs/
  │    ├── search/
  │    └── index.html  # redirects
  |
  ├── assets/
  ├── docs/
  ├── search/
  ├── index.html
  ├── robots.txt
  └── sitemap.xml
```


::: note
The prefixes don't need to be equal to the version numbers. They can be any string, for example:

```python
variants={
  "v1": docs_v1,
  "v2": docs_v2,
}
```

**However, they must be named like the folders in `content/`**.
:::

### 4. Enable the version selector

Go to the file `views/version_selector.jinja` and remove
the `{#` at the beginning and the `#}` at the end, so the selector appears in your documentation.

Add a link to the list of options in the version selector at `views/version_selector.jinja` and rebuild your current documentation.

```html+jinja {title="views/version_selector.jinja" hl_lines="7 8"}
<div class="version variant-popover">
    <button type="button" popovertarget="version-selector" tabindex="0">
        {{ site.version }}
    </button>
    <div class="popover" role="menu">
        <div>
            <a href="/1.0/" {% if site.version == "1.0" %}class="selected"{% endif %} tabindex="0">1.0</a>
            <a href="/0.5/" {% if site.version == "0.5" %}class="selected"{% endif %} tabindex="0">0.5</a>
        </div>
    </div>
</div>
{%- endif %}
```

----

That's it, you can now switch between versions in your documentation.

![Version selector](/assets/images/version-selector-light.png){ .only-light }
![Version selector](/assets/images/version-selector-dark.png){ .only-dark }
