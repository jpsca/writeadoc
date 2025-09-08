---
title: Images
icon: icons/image.svg
---

To add an image, use an exclamation mark (`!`), followed by the alt text in brackets, and the path or URL to the image asset in parentheses. You can optionally add a title in quotation marks after the path or URL.

/// example | An image

```md
![The San Juan Mountains are beautiful!](/assets/images/san-juan-mountains.jpg "San Juan Mountains")
```

![The San Juan Mountains are beautiful!](/assets/images/san-juan-mountains.jpg "San Juan Mountains")

///


## Light and dark mode

You can show different images for light and dark color schemes by using the `only-light` or `only-dark` classes.

/// example | Image, different for light and dark mode

```md
![Lamp diagram](/assets/images/diagram-light.png){ .only-light }
![Lamp diagram](/assets/images/diagram-dark.png){ .only-dark }
```

![Lamp diagram](/assets/images/diagram-light.png){ .only-light }
![Lamp diagram](/assets/images/diagram-dark.png){ .only-dark }

///

If you don't want to have two versions of the images, you can instead use the `invert` class, that invert
the colors of the image **only in dark mode**. It doesn't look great for some images, but it's good enough most of the time.

/// example | Image, inverted colors in and dark mode

```md
![Lamp diagram](/assets/images/diagram-light.png){ .invert }
```

![Lamp diagram](/assets/images/diagram-light.png){ .invert }

///


## Image alignment

If the screen is wide enough, you can align images to the left or right, by wrapping the content in a `<div markdown="1"></div>` tag and adding the "left" or "right" class to the image.

/// example | Image, aligned to the left

![Alt text](/assets/images/image.png){ .invert .left }

```md
<div markdown="1">

![Alt text](/assets/images/image.png){ .left }


Aliqua id elit sint ullamco cillum consequat.

Proident ad elit laboris consectetur duis sint proident voluptate
incididunt nulla excepteur culpa tempor.
</div>
```

///

/// example | Image, aligned to the right

![Alt text](/assets/images/image.png){ .invert .right }

```md
<div markdown="1">

![Alt text](/assets/images/image.png){ .right }

Aliqua id elit sint ullamco cillum consequat.

Proident ad elit laboris consectetur duis sint proident voluptate
incididunt nulla excepteur culpa tempor.
</div>
```

///

To center an image, just add the class

/// example | Image, centered

```md
![Alt text](/assets/images/image.png){ .center }

```

![Alt text](/assets/images/image.png){ .invert .center }
///


## Image captions

Unfortunately, the Markdown syntax doesn't provide native support for image captions, but you can use the [Markdown in HTML](/docs/md/markdown/html/#markdown-in-html) feature with literal `figure` and `figcaption` tags:

/// example | Image, centered

```md
<figure markdown="span">
![Alt text](/assets/images/image.png)
<figcaption>Image caption</figcaption>
</figure>
```

<figure markdown="span">
![Alt text](/assets/images/image.png){ .invert }
<figcaption>Image caption</figcaption>
</figure>

///


## Image links

To add a link to an image, enclose the Markdown for the image in brackets, and then add the link in parentheses.

/// example | A linked image

```md
[![Alt text](/assets/images/image.png "My title")](https://example.com/)
```

[![Alt text](/assets/images/image.png "My title"){ .invert }](https://example.com/)

///


## Forcing image size

You can force an image to have a specific width and/or height by adding attributes. Set just one of them to resize the image while preserving its aspect ratio, or set both to distort it.

/// example | Images with width/height

```md
![Alt text](/assets/images/image.png "My title"){ width=100 }

![Alt text](/assets/images/image.png "My title"){ width=300 height=50 }
```

![Alt text](/assets/images/image.png "My title"){ .invert width=100 }

![Alt text](/assets/images/image.png "My title"){ .invert width=300 height=50 }

///


## Lazy-loading images

Modern browsers provide [native support for lazy-loading images](https://caniuse.com/loading-lazy-attr) through the `loading=lazy` attribute, which falls back to normal eager-loading in browsers without support.

/// example | Image, centered

```md
![Alt text](/assets/images/opengraph.png){ loading=lazy }
```

![Alt text](/assets/images/opengraph.png){ loading=lazy width=600 }

///
