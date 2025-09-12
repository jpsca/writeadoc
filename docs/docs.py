from writeadoc import Docs


pages = [
    "intro.md",
    "pages.md",
    "autodoc.md",
    "languages.md",
    "versions.md",
    {
        "path": "markdown.md",
        "pages": [
            "markdown/blocks.md",
            "markdown/formatting.md",
            "markdown/links.md",
            "markdown/images.md",
            {
                "title": "Lists",
                "pages": [
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
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "WriteADoc",
        "base_url": "https://writeadoc.scaletti.dev/",
        "description": "Focus on your content and let WriteADoc take care of the rest",
        "lang": "en",
        "version": "0.1",
        "source_code": "https://github.com/jpsca/writeadoc/",
    },
)


if __name__ == "__main__":
    docs.cli()
