from writeadoc import Docs


pages = {
    "Welcome": [
        "welcome.md",
        "api/example.md",
    ],
}

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "Project Name",
        "description": "Description of your project",
        "lang": "en",
        "version": "1.0",
        "image": "/assets/images/opengraph.jpg",
        "source_url": "https://github.com/example/project",
        "base_url": "https://project.example.com",
        "help_url": "",
    },
)


if __name__ == "__main__":
    docs.cli()
