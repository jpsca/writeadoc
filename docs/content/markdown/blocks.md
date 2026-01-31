---
title: Block elements
icon: icons/blocks.svg
---

## Paragraphs

To create paragraphs, use a blank line to separate blocks of text.

::: div example
```md
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque at
faucibus quam, sit amet condimentum mi.

Donec tellus turpis, posuere sit amet sem vitae, blandit efficitur erat.
Sed faucibus mollis enim ac molestie.
```

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque at
faucibus quam, sit amet condimentum mi.

Donec tellus turpis, posuere sit amet sem vitae, blandit efficitur erat.
Sed faucibus mollis enim ac molestie.
:::


## Headers

To create a header, add number signs (#) in front of a word or phrase.
The number of number signs you use should correspond to the header level.
Always put a space between the number signs and the heading name, and use
blank lines before and after a header.

::: div example
```md
# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6
```

# Header 1 {skip-toc=""}

## Header 2 {skip-toc=""}

### Header 3 {skip-toc=""}

#### Header 4 {skip-toc=""}

##### Header 5 {skip-toc=""}

###### Header 6 {skip-toc=""}
:::


## Line breaks

To create a line break or new line, either add the HTML tag `<br>`, or end
a line with two or more spaces.

::: div example
```md
First line with the HTML tag after.<br>
And the next line.

First line with two spaces after.
And the next line.
```

First line with the HTML tag after.<br>
And the next line.

First line with two spaces after.
And the next line.
:::


## Blockquote

To create a blockquote, add a `>` at the beginning of each line.

::: div example
```md
> Dorothy followed her through many of the beautiful rooms
> in her castle.
```

> Dorothy followed her through many of the beautiful rooms
> in her castle.
:::


Blockquotes can contain multiple paragraphs. Add a `>` on the blank lines between paragraphs.

::: div example
```md
> Dorothy followed her through many of the beautiful rooms
> in her castle.
>
> The Witch bade her clean the pots and kettles and sweep the
> floor and keep the fire fed with wood.
```

> Dorothy followed her through many of the beautiful rooms
> in her castle.
>
> The Witch bade her clean the pots and kettles and sweep the
> floor and keep the fire fed with wood.
:::


## Horizontal Rules

To create a horizontal rule, use three or more asterisks (`***`),
dashes (`---`), or underscores (`___`) on a line by themselves.

::: div example
```md
***

---

_________________
```

The rendered output of all three looks identical:

---
:::
