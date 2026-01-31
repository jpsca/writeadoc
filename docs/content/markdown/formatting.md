---
title: Formatting
icon: icons/format.svg
---

## Emphasis

To italicize text, add one underscore (or one asteeisk) before and after a word or phrase.
To bold text, add two asterisks (or two underscores) before and after a word or phrase.

There cannot be spaces following the opening token(s) or preceding the closing token(s).

::: div example
```md
This **is bold** and __also this__

This _is italicized_ and *also this*

This * won't emphasize *
```

This **is bold** and __also this__

This _is italicized_ and *also this*

This * won't emphasize *
:::

When mixing bold and italic, stick with asterisks (**) for bold and underscores (_) for italics.

::: div example
```md
**_I'm italic and bold_ I am just bold.**

_**I'm bold and italic!** I am just italic._

_I'm italic. **I'm bold and italic.** I'm also just italic._
```

**_I'm italic and bold_ I am just bold.**

_**I'm bold and italic!** I am just italic._

_I'm italic. **I'm bold and italic.** I'm also just italic._
:::


## Code

To denote a word or phrase as code, enclose it in backticks (`).

::: div example
```md
To run the command, press `ENTER`.
```

To run the command, press `ENTER`.
:::

### Escaping Backticks

If the word or phrase you want to denote as code includes one or more backticks, you can escape it by enclosing the word or phrase in double backticks (``).

::: div example
```md
``Use `code` in your Markdown file.``
```

``Use `code` in your Markdown file.``
:::


## Sub- and superscripts

With this simple syntax, text can be subscripted and superscripted, which is more convenient than directly using the corresponding `sub` and `sup` HTML tags.

To make a subscript, surround the content with a single `~`. To make a superscript, surround the content with `^`. In both cases, if you need to include spaces, you must escape them.

::: div example
```md
CH~3~CH~2~OH

text~a\ subscript~

a^2^ + 2ab + b^2^

text^a\ superscript^
```

CH~3~CH~2~OH

text~a\ subscript~

a^2^ + 2ab + b^2^

text^a\ superscript^
:::


## Highlighting changes

Text changes can be highlighted with a simple syntax, which is more convenient than directly using the corresponding `mark`, `ins`, and `del` HTML tags.

To highlight text, surround it with double `=`. To highlight an insertion, use double `^`, and to highlight a deletion, use double `~`.

::: div example
```md
- ==This was marked (highlight)==
- ^^This was inserted (underline)^^
- ~~This was deleted (strikethrough)~~
```

- ==This was marked (highlight)==
- ^^This was inserted (underline)^^
- ~~This was deleted (strikethrough)~~
:::
