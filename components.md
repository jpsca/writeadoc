---
title: Components
description: Declaring and using components.
copyright: Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
---

Components are simple text files that look like regular Jinja templates

## Declaring and Using Components

**First**, components must be placed inside a folder registered in the catalog or a subfolder of it.

```python
catalog.add_folder("myapp/components")
```

You can name that folder whatever you want (not just "components"). You can also add more than one folder:

```python
catalog.add_folder("myapp/layouts")
catalog.add_folder("myapp/components")
```

If you end up having more than one component with the same name, the one in the first folder will take priority.

**Second**, they must have a ".jinja" extension. This also helps code editors automatically select the correct language syntax for highlighting. However, you can configure this extension in the catalog.

**Third**, the filename must be either PascalCased (like Python classes) or "kebab-cased" (lowercase with words separated by dashes).

The PascalCased name of the file (minus the extension) is always how you call the component (even if the filename is kebab-cased). This is how JinjaX differentiates a component from a regular HTML tag when using it.

For example, if the file is "components/PersonForm.jinja":

```bash
└ myapp/
  ├── app.py
  ├── components/
        └─ PersonForm.jinja
```

The name of the component is "PersonForm" and can be called like this:

From Python code or a non-component template:

- `catalog.render("PersonForm")`

From another component:

- `<PersonForm> some content </PersonForm>`, or
- `<PersonForm />`


If you prefer you can also choose to use kebab-cased filenames:

```bash
└ myapp/
  ├── app.py
  ├── components/
        └─ person-form.jinja
```

The name of the component **will still be "PersonForm"** and you will use it in the same way as before.

/// warning
Do not mix PascalCased files with kebab-cased files. Choose a name format you like
and stick with it.
///

### Subfolders

If the component is in a subfolder, the name of that folder becomes part of its name too:

```bash
└ myapp/
  ├── app.py
  ├── components/
        └─ Person/
            └─ Form.jinja
```

A "components/person/PersonForm.jinja" component is named "Person.Form", meaning the name of the subfolder and the name of the file separated by a dot. This is the full name you use to call it:

From Python code or a non-component template:

- `catalog.render("Person.Form")`

From another component:

- `<Person.Form> some content </Person.Form>`, or
- `<Person.Form />`

You can also use kebab-cased filenames in subfolders and call them the same way:

```bash
└ myapp/
  ├── app.py
  ├── components/
        └─ password-reset/
            └─ form.jinja
```

From Python code or a non-component template:

- `catalog.render("PasswordReset.Form")`

From another component:

- `<PasswordReset.Form> some content </PasswordReset.Form>`, or
- `<PasswordReset.Form />`

## Anatomy of a Component

<a href="/assets/images/anatomy-en.svg" target="_blank" style="display:block; text-align:center;">
  <img src="/assets/images/anatomy-en.svg" width="940" height="840" style="width:100%;max-width:940px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);" />
</a>
