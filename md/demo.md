# Formatting

## Emphasis

To italicize text, add one asterisk or one underscore before and after a word or phrase.
To bold text, add two asterisks or two underscores before and after a word or phrase.

There cannot be spaces following the opening token(s) or preceding the closing token(s).

```{note} Miau?
This **is bold**, __and also this__

This *is italicized*, _and also this_

This * won't emphasize *
```

### Bold and Italic

When mixing bold and italic, WriteADoc will try to prioritize the most sensible option when nesting bold (**) within italic (*) and vice versa.

```{note}

***I'm italic and bold* I am just bold.**

***I'm bold and italic!** I am just italic.*

*I'm italic. **I'm bold and italic.** I'm also just italic.*
```


```{note}
:open: True

```md
__This will all be bold __because of the placement of the center underscores.__

__This will all be bold __ because of the placement of the center underscores.__

__This will NOT all be bold__ because of the placement of the center underscores.__

__This will all be bold_ because the token is less than that of the surrounding.__
```

__This will all be bold __because of the placement of the center underscores.__

__This will all be bold __ because of the placement of the center underscores.__

__This will NOT all be bold__ because of the placement of the center underscores.__

__This will all be bold_ because the token is less than that of the surrounding.__
```
