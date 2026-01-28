---
title: Ordered Lists
icon: icons/list-ol.svg
---

To create an ordered list, add line items with numbers followed by periods. You can also use `#` instead of numbers.
WriteADoc extends the list handling formats to support parenthesis-style lists along with additional ordered formats.

### Numerical

::: div example
```md
1. First item
2. Second item
#. Third item
```

1. First item
2. Second item
#. Third item
:::

### Alphabetical

::: div example
For uppercase, use two spaces after the dot (or a parenthesis instead).

```md
a. First item
b. Second item
c. Third item

A.  First item
B.  Second item
C.  Third item
```

a. First item
b. Second item
c. Third item

A.  First item
B.  Second item
C.  Third item
:::

### Roman numerals

::: div example
For uppercase, use two spaces after the dot (or a parenthesis instead).

```md
i. First item
ii. Second item
iii. Third item

I.  First item
II.  Second item
III.  Third item

```

i. First item
ii. Second item
iii. Third item

I.  First item
II.  Second item
III.  Third item
:::


## Nested lists

Indent with two spaces to create a nested list.

::: div example
```md
1) Item 1
2) Item 2
  i. Item 1
  ii. Item 2
    a. Item a
    b. Item b
      #. Item 1
      #. Item 2
```

1) Item 1
2) Item 2
  i. Item 1
  ii. Item 2
    a. Item a
    b. Item b
      #. Item 1
      #. Item 2
:::


## Features

- Supports ordered lists with either a trailing dot or a single right parenthesis: `1.` or `1)`.
- Supports ordered lists with Roman numeral formats, both lowercase and uppercase. Uppercase is treated as a different list type than lowercase.
- Supports ordered lists with alphabetical format, both lowercase and uppercase. Uppercase is treated as a different list type than lowercase.
- Supports a generic ordered list marker via `#.` or `#)`. These can be used in place of numerals and will inherit the type of the current list as long as they use the same convention (`.` or `)`). If used to start a list, decimal format will be assumed.
- Using a different list type will start a new list. Trailing dot vs. parenthesis are treated as separate types.
- Ordered lists are sensitive to the starting value and can restart a list or create a new list using the first value in the list.


## Rules

### 1.  A new list will be created if the list type changes

This occurs with:

a. A switch between unordered and ordered.

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

b. A change from using a trailing dot to a single right parenthesis.

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

c. A change between using uppercase and lowercase.

::: div example
```md
a.  Item a
b.  Item a
A.  Item A
B.  Item B
```

a.  Item a
b.  Item a
A.  Item A
B.  Item B
:::

d. A change in ordered type: numerical, Roman numeral, alphabetical, or generic.

::: div example
```md
#.  Item 1
#.  Item 2
a.  Item a
b.  Item b
1.  Item 1
2.  Item 2
```

#.  Item 1
#.  Item 2
a.  Item a
b.  Item b
1.  Item 1
2.  Item 2
:::

### 2. Generic list items inherit the type from the current list and, if starting a new list, will assume the decimal type

List items following a generic list will not cause a new list as long as the list item is consistent with the current list type.

::: div example
```md
i.  item i
#.  item ii
#.  item iii
iv. item iv
```

i.  item i
#.  item ii
#.  item iii
iv. item iv
:::

### 3. If using uppercase list markers, a list marker consisting of a single uppercase letter followed by a dot will require two spaces after the marker instead of the usual one, to avoid false positive matches with names that start with an initial

::: div example
```md
B. Russell was an English philosopher.

A.  This is a list.
```

B. Russell was an English philosopher.

A.  This is a list.
:::

### 4. If a single letter is used to start a list, it is assumed to be an alphabetical list unless the first letter is `i` or `I`

::: div example
```md
h. Item h
i. Item i
j. Item j

---

i. Item 1
ii. Item 2
iii. Item 3
```

h. Item h
i. Item i
j. Item j

---

i. Item 1
ii. Item 2
iii. Item 3
:::
