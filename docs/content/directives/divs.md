---
title: Divs
icon: icons/blocks.svg
---

This is a generic wrapper with HTML classes to customize your documents.

Instead of a title, the text after the name will be added as classes:

```md
::: div my-class another-class
Any markdown content
:::
```

will render as

```html
<div class="my-class another-class">
<p>Any markdown content</p>
</div>
```
