---
title: Unordered Lists
---

To create an unordered list, add dashes (-), asterisks (*), or plus signs (+) in front of line items.

/// example |

```md
- First item
- Second item
- Third item
- Fourth item
```

- First item
- Second item
- Third item
- Fourth item

///

Indent one or more items to create a nested list.

/// example |

```md
- item 1
  * item A
  * item B
    more text
    + item a
    + item b
    + item c
  * item C
- item 2
- item 3
```

- item 1
  * item A
  * item B
    more text
    + item a
    + item b
    + item c
  * item C
- item 2
- item 3

///

## Starting Unordered List Items With Numbers

If you need to start an unordered list item with a number followed by a period, you can use a backslash (\) to escape the period.

/// example |

```md
- 1979\. A great year!
- I think 1983 was second best.
```

- 1979\. A great year!
- I think 1983 was second best.

///

## List items with paragraphs

To add another element in a list while preserving the continuity of the list, indent the element **four spaces** or **one tab**, as shown in the following examples.

/// example | Paragraphs

```md
* This is the first list item.
* Here's the second list item.

    I need to add another paragraph below the second list item.

* And here's the third list item.
```

* This is the first list item.
* Here's the second list item.

    I need to add another paragraph below the second list item.

* And here's the third list item.

///

<!-- -->

/// example | Blockquotes

```md
* This is the first list item.
* Here's the second list item.

    > A blockquote would look great below the second list item.

* And here's the third list item.
```

* This is the first list item.
* Here's the second list item.

    > A blockquote would look great below the second list item.

* And here's the third list item.

///

<!-- -->

/// example | Images

```md
1. Open the file containing the Linux mascot.
2. Marvel at its beauty.

    ![Tux, the Linux mascot](/assets/images/tux.png)

3. Close the file.
```

1. Open the file containing the Linux mascot.
2. Marvel at its beauty.

    ![Tux, the Linux mascot](/assets/images/tux.png)

3. Close the file.

///

