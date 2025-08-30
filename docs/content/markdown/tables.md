---
title: Tables
icon: icons/table.svg
---

To add a table, use three or more hyphens (`---`) to create each column’s header, and use pipes (`|`) to separate each column. You can also add a pipe on either end of the row, but it is not necessary.

/// example | Table

```md

| Method      | Description     |
| ----------- | --------------- |
| `GET`       | Fetch resource  |
| `PUT`       | Update resource |
| `DELETE`    | Delete resource |

```

| Method      | Description     |
| ----------- | --------------- |
| `GET`       | Fetch resource  |
| `PUT`       | Update resource |
| `DELETE`    | Delete resource |

///

You don't have to make each cell the same width, but it looks clearer if you do.

/// tip

Creating tables with hyphens and pipes can be tedious. To speed up the process, try using the [Markdown Tables Generator](https://www.tablesgenerator.com/markdown_tables). Build a table using the graphical interface, and then copy the generated Markdown-formatted text into your file.

///


## Alignment

You can align text in the columns to the left, right, or center by adding a colon (`:`) to the left, right, or on both sides of the hyphens within the header row.

/// example | Table with aligned columns

```md

| Syntax      | Description | Test Text     |
| :---        |    :----:   |          ---: |
| Header      | Title       | Here's this   |
| Paragraph   | Text        | And more      |

```

| Syntax      | Description | Test Text     |
| :---        |    :----:   |          ---: |
| Header      | Title       | Here's this   |
| Paragraph   | Text        | And more      |

///
