from writeadoc import Docs


pages = [
    {
        "title": "Quickstart",
        "pages": [
            "quickstart/setup.md",
            "quickstart/config.md",
            "quickstart/write.md",
        ]
    },
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
    },
    "autodoc.md",
    "languages.md",
    "versions.md",
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "WriteADoc",
        "base_url": "https://writeadoc.scaletti.dev",
        "lang": "en",
        "description": "Documentation your users will love",
        "source_code": "https://github.com/jpsca/writeadoc/",
    },
)


if __name__ == "__main__":
    docs.cli()
