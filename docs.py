from writeadoc import Docs
import theme


pages = {
    "Overview": [
        "overview/intro.md",
        "overview/motivation.md",
    ],
    "Guides": [
        "components.md",
        "arguments.md",
        "organization.md",
        "slots.md",
        "css_and_js.md",
    ],
}

docs = Docs(
    pages=pages,
    theme=theme,
    base_url="https://jinjax.scaletti.dev/",
)


if __name__ == "__main__":
    docs.cli()
