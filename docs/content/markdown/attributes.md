---
title: Attributes Lists
icon: icons/attrs.svg
---

The Attribute Lists syntax allows you to define attributes on various HTML elements in Markdown's output.
An example attribute list might look like this:

```md
{ #someid .someclass somekey='some value' }
```

- A word which starts with a hash `#` will set the id of an element.
- A word which starts with a dot `.` will be added to the list of classes assigned to an element.
- A key/value pair `somekey="some value"` will assign that pair to the element.

Be aware that while the dot syntax will add to a class, using key/value pairs will always override any previously defined attribute.

Curly braces can be backslash-escaped to avoid being identified as an attribute list.

```md
\{ not an attribute list }
```


## Block Level

To define attributes for a block-level element, the attribute list should be placed on the last line of the block by itself.

```md
This is a paragraph.
{ #an_id .a_class }
```

The above results in the following code:

```html
<p id="an_id" class="a_class">This is a paragraph.</p>
```

An exception is headers, as they are only ever allowed on one line.

```md
### A hash style header { .break }
```

The above results in the following code:

```html
<h3 class="break">A hash style header</h3>
```


## Inline

To define attributes on inline elements, the attribute list should be placed immediately after the inline element with no whitespace.

```md
[link](http://example.com){: class="foo bar" title="Some title!" }
```

The above results in the following output:

```html
<p><a href="http://example.com" class="foo bar" title="Some title!">link</a></p>
```

Attribute lists can be defined on table _cells_ (but not on tables themselves). To differentiate attributes for an inline element from attributes for the containing cell, the attribute list must be separated from the content by at least one space and placed at the end of the cell content. As table cells can only ever be on a single line, the attribute list must remain on the same line as the content of the cell.

```md
| set on td    | set on em   |
|--------------|-------------|
| *a* { .foo } | *b*{ .foo } |
```

The above example results in the following output:

```html
<table>
  <thead>
    <tr>
      <th>set on td</th>
      <th>set on em</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="foo"><em>a</em></td>
      <td><em class="foo">b</em></td>
    </tr>
  </tbody>
</table>
```

Note that in the first column, the attribute list is preceded by a space; therefore, it is assigned to the table cell (`<td>` element). However, in the second column, the attribute list is not preceded by a space; therefore, it is assigned to the inline element (`<em>`) that immediately precedes it.

Attribute lists may also be defined on table header cells (`<th>` elements) in the same manner.


## Limitations

There are a few types of elements with which attribute lists do not work, most notably those HTML elements that are not represented in Markdown text, but only implied.

For example, the `ul` and `ol` elements do not exist in Markdown. They are only implied by the presence of list items (`li`).
There is no way to use an attribute list to define attributes on implied elements, including but not limited to: `ul`, `ol`, `dl`, `blockquote`, `table`, `thead`, `tbody`, and `tr`.

As a workaround, because Markdown is a subset of HTML, anything that cannot be expressed in Markdown can always be expressed with raw HTML directly.
