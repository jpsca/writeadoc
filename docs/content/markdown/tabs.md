---
title: Tabs
icon: icons/tab.svg
---

Some parts of your documentation might become clear by organzing them in tabs, such as language-specific code snippets (e.g., tabs for Python, JavaScript, etc.) or an example that uses several files (e.g. a tabs for HTML, CSS, and JavaScript of a component)

A tab is defined using the `:::` syntax and the name `tab`. Tabs should also specify the tab title in the
header. Consecutive tabs will automatically be grouped.

:::: div example
```md
::: tab | Tab 1 title
Tab 1 content
:::

::: tab | Tab 2 title
Tab 2 content
:::
```

::: tab | Tab 1 title
Tab 1 content
:::

::: tab | Tab 2 title
Tab 2 content
:::
::::

If you want to have two tab containers right after each other, you specify a hard break that will force the specified tab to start a brand new tab container.

:::: div example
```md
::: tab | Tab A title
Tab A content
:::

::: tab | Tab B title
Tab B content
:::

::: tab | Tab C Title
:new: true

Will be part of a separate, new tab group.
:::
```

::: tab | Tab A title
Tab A content
:::

::: tab | Tab B title
Tab B content
:::

::: tab | Tab C title
:new: true

Will be part of a separate, new tab group.
:::
::::

If desired, you can specify a tab to be selected by default with the `select` option.

```md
::: tab | Tab 1 title
Tab 1 content
:::

::: tab | Tab 2 title
:select: True

Tab 2 should be selected by default.
:::
```

As with other blocks, you can always add new classes, and id or other attributes via the options.

```md
::: tab | Some title
:class: class-name
:id: id-name

Some content
:::
```
