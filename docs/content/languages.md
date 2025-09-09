---
title: Multiple languages
icon: icons/language.svg
---

WriteADoc supports internationalization and managing documentation in multiple languages out of the box.

## Setting the language

To set your documentation language, use the `lang` argument with a language code ("en" for English, "es" for Spanish, "fr" for French, etc.). English is the default, so you don't need to set it explicitly.

```python {hl_lines="5 6"}
docs = Docs(
    __file__,
    pages=pages,
    views=views,
    site={
        lang: "es",
        ...
    },
)
```

This language will be used for two things: translating the few hardcoded strings in the views, and fine-tuning the search so it works better.

For a very small list of languages — Danish (da), German (de), Spanish (es), French (fr), Italian (it), and Portuguese (pt) — this will be done automatically. But don't worry if yours is not in the list, because it's very simple to add support for a new one.

### Translating your views

...

When adding new hardcoded text to your views (meaning, not coming from the markdown files), you can add them to the `strings` dict. However, this is only useful if you want to have variants of your documentation in other languages (see the section ["Working with multiple languages"](#working-with-multiple-languages) later on this page).

You can also add translations for URLs or paths of images, videos, etc. Or you can use the `site.lang` attribute instead:

```html+jinja
<video href="myvideo_{{ site.lang }}.mp4"></video>
```

### Making the search aware of your language

WriteADoc uses [Lunr.js](https://lunrjs.com/) for searching without an external service. If your language is not included with WriteADoc by default, you must
download the `lunr.[YOUR LANGUAGE].min.js` support file [from here](https://github.com/MihaiValentin/lunr-languages/tree/master/min). For example, for Korean you would download the file `lunr.ko.min.js`.
Save the file to `assets/js/`.

You might want to delete the files already there for languages you are not going to use.

## Working with multiple languages

variants

language selector

```html+jinja {title="views/language_popover.jinja" linenums="7"}
<div id="language-selector" popover="auto">
    <div>
        <a href="/" {% if site.lang == "en" %}class="selected"{% endif %}>English</a>
        <a href="/es/" {% if site.lang == "es" %}class="selected"{% endif %}>Español</a>
    </div>
</div>
```