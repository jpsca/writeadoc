from pathlib import Path

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
        "title": "Markdown",
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
            "markdown/attributes.md",
            "markdown/html.md",
        ],
    },
    {
        "path": "directives/index.md",
        "pages": [
            "directives/admonitions.md",
            "directives/figures.md",
            "directives/tabs.md",
            "directives/divs.md",
        ],
    },
    "autodoc.md",
    "languages.md",
    "versions.md",
    "api.md",
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "WriteADoc",
        "base_url": "https://writeadoc.scaletti.dev",
        "lang": "en",
        "version": "1.0",
        "description": "Documentation your users will love",
        "source_code": "https://github.com/jpsca/writeadoc/",
    },
)
docs.catalog.add_folder(Path(__file__).parent / "comp")


if __name__ == "__main__":
    docs.cli()
