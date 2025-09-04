"""
# WriteaDoc Documentation

- `python docs.py run` to start a local server with live reload.
- `python docs.py build` to build the documentation for deployment.

"""
from writeadoc import Docs


pages = {
    "Welcome": [
        "welcome.md",
        {
            "Subsection": [
                "sub/lorem.md",
                "sub/ipsum.md",
            ],
        }
    ],
}

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "Project Name",
        "description": "Description of your project",
        "base_url": "https://project.example.com",
        "lang": "en",
        "version": "1.0",
    },
)


if __name__ == "__main__":
    docs.cli()
