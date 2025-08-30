---
title: Formatting
icon: icons/format.svg
---

## Emphasis

To italicize text, add one asterisk or one underscore before and after a word or phrase.
To bold text, add two asterisks or two underscores before and after a word or phrase.

There cannot be spaces following the opening token(s) or preceding the closing token(s).

/// example |

```md
This **is bold**, __and also this__

This *is italicized*, _and also this_

This * won't emphasize *
```

This **is bold**, __and also this__

This *is italicized*, _and also this_

This * won't emphasize *

///

### Bold and Italic

When mixing bold and italic, WriteADoc will try to prioritize the most sensible option when nesting bold (**) within italic (*) and vice versa.

/// example |

```md
***I'm italic and bold* I am just bold.**

***I'm bold and italic!** I am just italic.*

*I'm italic. **I'm bold and italic.** I'm also just italic.*
```

***I'm italic and bold* I am just bold.**

***I'm bold and italic!** I am just italic.*

*I'm italic. **I'm bold and italic.** I'm also just italic.*

///

Complex examples:

/// example |

```md
__This will all be bold __because of the placement of the center underscores.__

__This will all be bold __ because of the placement of the center underscores.__

__This will NOT all be bold__ because of the placement of the center underscores.__

__This will all be bold_ because the token is less than that of the surrounding.__
```

__This will all be bold __because of the placement of the center underscores.__

__This will all be bold __ because of the placement of the center underscores.__

__This will NOT all be bold__ because of the placement of the center underscores.__

__This will all be bold_ because of the token is less than that of the surrounding.__

///


## Code

To denote a word or phrase as code, enclose it in backticks (`).

/// example |

```md
To run the command, press `ENTER`.
```

To run the command, press `ENTER`.

///

### Escaping Backticks

If the word or phrase you want to denote as code includes one or more backticks, you can escape it by enclosing the word or phrase in double backticks (``).

/// example |

```md
``Use `code` in your Markdown file.``
```

``Use `code` in your Markdown file.``

///


## Sub- and superscripts

With this simple syntax, text can be subscripted and superscripted, which is more convenient than directly using the corresponding `sub` and `sup` HTML tags.

To make a subscript, surround the content with a single `~`. To make a superscript, surround the content with `^`. In both cases, if you need to include spaces, you must escape them.

/// example |

```md
CH~3~CH~2~OH

text~a\ subscript~

a^2^ + 2ab + b^2^

text^a\ superscript^
```

CH~3~CH~2~OH

text~a\ subscript~

///


## Highlighting changes

Text changes can be highlighted with a simple syntax, which is more convenient than directly using the corresponding `mark`, `ins`, and `del` HTML tags.

To highlight text, surround it with double `=`. To highlight an insertion, use double `^`, and to highlight a deletion, use double `~`.

/// example |

```md
- ==This was marked (highlight)==
- ^^This was inserted (underline)^^
- ~~This was deleted (strikethrough)~~
```

- ==This was marked (highlight)==
- ^^This was inserted (underline)^^
- ~~This was deleted (strikethrough)~~

///


## Symbols

Although Markdown doesn't have native support for including special symbols, WriteADoc makes it easy to create *some* special characters such as trademarks, arrows, fractions, etc.

| Markdown         | Result
| ---------------- | -------------
| `(tm)`           | (tm)
| `(c)`            | (c)
| `(r)`            | (r)
| `c/o`            | c/o
| `+/-`            | +/-
| `-->`            | -->
| `<--`            | <--
| `<-->`           | <-->
| `=/=`            | =/=
| `1/2, 1/4, etc.` | 1/2, 1/4, etc.
| `1st 2nd etc.`   | 1st 2nd etc.

For anything else, you can use HTML code or Unicode characters: 👈 😍 👍 🐱 👀.
