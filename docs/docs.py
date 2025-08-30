from writeadoc import Docs


pages = {
    "Overview": [
        "overview/intro.md",
        "overview/autodoc.md",
        "overview/languages.md",
        "overview/versions.md",
    ],
    "Markdown": [
        "markdown/intro.md",
        "markdown/blocks.md",
        "markdown/formatting.md",
        "markdown/links.md",
        "markdown/images.md",
        {
            "Lists": [
                "markdown/lists/unordered.md",
                "markdown/lists/ordered.md",
                "markdown/lists/tasks.md",
            ]
        },
        "markdown/code.md",
        "markdown/tables.md",
        "markdown/admonitions.md",
        "markdown/attributes.md",
        "markdown/html.md",
    ],
}

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "WriteADoc",
        "description": "Write your documentation",
        "lang": "en",
        "version": "1.0",
        "image": "/assets/images/opengraph.png",
        "source_url": "https://github.com/jpsca/writeadoc",
        "base_url": "https://writeadoc.scaletti.dev/",
        "help_url": "",
    },
)


if __name__ == "__main__":
    docs.cli()
