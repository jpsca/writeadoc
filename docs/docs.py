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
        "name": "Project Name",
        "base_url": "https://project.example.com",
        "version": "1.0",
        "lang": "en",
        "description": "Description of your project",
        "source_code": "https://github.com/yourusername/yourproject/",
    },
)


if __name__ == "__main__":
    docs.cli()
