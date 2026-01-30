---
title: Attributes Lists
icon: icons/attrs.svg
---

The Attribute Lists syntax allows you to define attributes on various HTML elements in Markdown output.
An example attribute list might look like this:

```md
{ #someid .someclass somekey='some value' }
```

- A word that starts with a hash `#` will set the ID of an element.
- A word that starts with a dot `.` will be added to the list of classes assigned to an element.
- A key/value pair `somekey="some value"` will assign that pair to the element.

Be aware that while the dot syntax will add to the class attribute, using key/value pairs will always override any previously defined attribute.

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

## Inline

To define attributes on inline elements, the attribute list should be placed immediately after the inline element, with no spaces in between.

```md
[link](http://example.com){ class="foo bar" title="Some title!" }
```

The above results in the following output:

```html
<p><a class="foo bar" href="http://example.com" title="Some title!">link</a></p>
```

## Limitations

There are a few types of elements with which attribute lists do not work, most notably those HTML elements that are not represented in Markdown text, but only implied. The attributes list feature **does not work** on:

- Lists and list items: `ul`, `ol`, `dl`, and `li`
- Block quotes,
- Tables and table elements.

As a workaround, because Markdown is a subset of HTML, anything that cannot be expressed in Markdown can always be expressed directly with raw HTML.
