---
title: Directives
---

WriteADoc add to the  common markdwown syntax some popular extensions it calls "directives". A directive starts and end with at least three periods `:::` and a name:

```markdown
::: name | Some text
:option1:=value1

Markdown content
:::
```

The `|` after the name is optional

## Nested directives

You can nest directives to add, for example, an admonition inside an div. To do so just use more ":" to the outer directive:

```md
:::: div wrapper

::: note
Hello
:::

::::
```
