---
title: Ordered Lists
icon: icons/list-ol.svg
---

To create an ordered list, add line items with numbers followed by periods or parenthesis.

::: div example
```md
1. First item
2. Second item
3. Third item
```

1. First item
2. Second item
3. Third item
:::

You can also start the list with a different number

::: div example
```md
6. apples
7. oranges
8. pears
```

6. apples
7. oranges
8. pears
:::

## Nested lists

Indent with two spaces to create a nested list.

::: div example
```md
1) Item 1
2) Item 2
  1. Item 1
  2. Item 2
    1. Item a
    2. Item b
      1. Item 1
      2. Item 2
```

1) Item 1
2) Item 2
  1. Item 1
  2. Item 2
    1. Item a
    2. Item b
      1. Item 1
      2. Item 2
:::


## Adjacent lists

A new list will be created if the list type changes. This occurs with:

**a. A switch between unordered and ordered.**

::: div example
```md
-   Item 1
-   Item 2
1.  Item 1
2.  Item 2
```

-   Item 1
-   Item 2
1.  Item 1
2.  Item 2
:::

**b. A change from using a trailing dot to a single right parenthesis.**

::: div example
```md
1.  Item 1
1.  Item 2
1)  Item 1
2)  Item 2
```

1.  Item 1
1.  Item 2
1)  Item 1
2)  Item 2
:::
