import re
import typing as t
from pathlib import Path
from uuid import uuid4

import jx
import markdown
from markupsafe import Markup

from . import search, utils
from .autodoc import Autodoc
from .types import (
    NavItem,
    PageData,
    PageRef,
    TMetadata,
    TUserPages,
    TUserSection,
)
from .utils import logger


if t.TYPE_CHECKING:
    from .main import Docs


RX_AUTODOC = re.compile(r"<p>\s*:::\s+([\w\.\:]+)((?:\s+\w+=[\w\*_]+)*)\s*</p>")


class PagesProcessor:
    docs: "Docs"
    md_renderer: markdown.Markdown
    autodoc: Autodoc

    nav_items: list[NavItem]
    pages: list[PageData]

    def __init__(self, docs: "Docs"):
        """Pages processor
        """
        self.docs = docs
        self.md_renderer = markdown.Markdown(
            extensions=[*utils.DEFAULT_MD_EXTENSIONS],
            extension_configs={**utils.DEFAULT_MD_CONFIG},
            output_format="html",
            tab_length=2,
        )
        self.autodoc = Autodoc()
        self.pages = []

    def run(self, user_pages: TUserPages) -> tuple[list[NavItem], list[PageData]]:
        """Recursively process the given pages list and returns navigation and flat page list.

        Input:

        ```python
        pages= [
            "intro.md",
            {
                "title": "Getting Started",
                "icon": "icons/rocket.svg",
                "pages": [
                    "start/installation.md",
                    "start/usage.md",
                    {
                        "title": "Migrating from MkDocs",
                        "path": "start/migrating.md",
                        "pages": [
                            "start/migrating/configuration.md",
                            "start/migrating/themes.md",
                        ],
                    },
                ]
            },
        ]
        ```

        Output:

        ```python
        # nav (actually a list of NavItem objects, not dicts)
        [
            {
                "id": "intro",
                "title": "Introduction",
                "url": "/docs/intro/",
                "icon": "",
                "pages": []
            },
            {
                "id": "65139efb38a24794b11c253e3aa72fc2",
                "title": "Getting Started",
                "icon": "icons/rocket.svg",
                "pages": [
                    {
                        "id": "start-installation",
                        "title": "Installation",
                        "url": "/docs/start/installation/",
                        "icon": "",
                        "pages": []
                    },
                    {
                        "id": "start-usage",
                        "title": "Usage",
                        "url": "/docs/start/usage/",
                        "icon": "",
                        "pages": []
                    },
                {
                    "id": "6513943434324794b11c253e3aa72fa3",
                    "title": "Migrating from MkDocs",
                    "url": "/docs/start/migrating/",
                    "icon": "",
                    "pages": [
                        {
                            "id": "start-migrating-configuration",
                            "title": "Configuration",
                            "url": "/docs/start/migrating/configuration/",
                            "icon": "icons/cog.svg",
                            "pages": []
                        },
                        {
                            "id": "start-migrating-themes",
                            "title": "Themes",
                            "url": "/docs/start/migrating/themes/",
                            "icon": "icons/themes.svg",
                            "pages": []
                        },
                    ]
                },
                ]
            },
        ]
        ```

        ```python
        # pages
        [
            <Page /docs/intro/>,
            <Page /docs/start/installation/>,
            <Page /docs/start/usage/>,
            <Page /docs/start/migrating/>,
            <Page /docs/start/migrating/configuration/>,
            <Page /docs/start/migrating/themes/>,
        ]
        ```

        """
        self.pages = []

        index_page = self.process_index_page()
        if index_page:
            self.pages.append(index_page)

        nav = self.process_items(user_pages)
        self.set_prev_next()
        self.set_search_data()
        return nav, self.pages

    def process_index_page(self) -> PageData | None:
        if self.docs.skip_home:
            return None

        if not (self.docs.views_dir / "index.jinja").exists():
            logger.warning("No index.jinja view found.")
            return None

        outpath = self.docs.build_dir / self.docs.prefix / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.docs.prefix}/" if self.docs.prefix else "/"

        md_index = self.docs.content_dir / self.docs.prefix / "index.md"
        if md_index.exists():
            source, meta = self.read_file(md_index)
            html = self.render_markdown(source, meta)
            meta.setdefault("id", "index")
            meta.setdefault("title", self.docs.site.name)
            meta.setdefault("view", "index.jinja")

            return PageData(
                url=url,
                meta=meta,
                source=source,
                content=Markup(html),
                filepath=md_index,
                toc=getattr(self.md_renderer, "toc_tokens", []),
            )

        # Just render the template page
        return PageData(
            url=url,
            meta={
                "id": "index",
                "title": self.docs.site.name,
                "view": "index.jinja",
            },
        )

    def process_items(
        self,
        user_pages: TUserPages,
        section_title: str = "",
        section_url: str = "",
        parents: tuple[str, ...] = (),
    ) -> list[NavItem]:
        items = []

        for user_page in user_pages:
            # Page
            if isinstance(user_page, str):
                item = self.process_page(
                    user_page,
                    section_title=section_title,
                    section_url=section_url,
                    parents=parents,
                )
                items.append(item)

            # Section
            elif isinstance(user_page, dict):
                item = self.process_section(
                    user_page,
                    section_title=section_title,
                    section_url=section_url,
                    parents=parents,
                )
                items.append(item)

            else:
                raise ValueError(f"Invalid page entry: {user_page}")

        return items

    def process_section(
        self,
        user_page: TUserSection,
        section_title: str = "",
        section_url: str = "",
        parents: tuple[str, ...] = (),
    ) -> NavItem:
        user_pages = user_page.get("pages", [])

        if not isinstance(user_pages, list) or not user_pages:
            raise ValueError(f"Section entry has invalid or empty 'pages': {user_page}")

        title = user_page.get("title")
        icon = user_page.get("icon") or ""
        closed = bool(user_page.get("closed", False))
        url = ""

        id = user_page.get("id") or f"s-{uuid4().hex}"
        parents = parents + (id, )

        sec_path = user_page.get("path")
        if sec_path:
            item = self.process_page(
                sec_path,
                section_title=section_title,
                section_url=section_url,
                parents=parents,
            )
            title = title or item.title
            icon = icon or item.icon
            url = item.url

        if not title:
            raise ValueError(f"Section entry is missing 'title': {user_page}")

        pages = self.process_items(
            user_pages,
            section_title=title,
            section_url=url,
            parents=parents,
        )
        return NavItem(
            title=title,
            id=id,
            url=url,
            icon=icon,
            pages=pages,
            closed=closed
        )

    def process_page(
        self,
        filename: str,
        section_title: str = "",
        section_url: str = "",
        parents: tuple[str, ...] = (),
    ) -> NavItem:
        url = f"/docs/{Path(filename).with_suffix('').as_posix().strip('/')}/"
        if self.docs.prefix:
            url = f"/{self.docs.prefix}{url}"

        filepath = self.docs.content_dir / filename
        source, meta = self.read_file(filepath)
        try:
            html = self.render_markdown(source, meta)
        except Exception as err:
            raise RuntimeError(f"Error processing {filepath}") from err

        page = PageData(
            url=url,
            section_title=section_title,
            section_url=section_url,
            meta=meta,
            source=source,
            content=Markup(html),
            filepath=filepath,
            toc=getattr(self.md_renderer, "toc_tokens", []),
            parents=parents,
        )
        self.pages.append(page)

        return NavItem(
            title=page.title,
            id=page.id,
            url=page.url,
            icon=page.icon,
        )

    def read_file(self, filepath: Path) -> tuple[str, TMetadata]:
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        logger.debug("Processing page: %s", filepath.relative_to(self.docs.content_dir))
        source = filepath.read_text(encoding="utf-8")
        source, meta = utils.extract_metadata(source)
        return source, meta

    def render_markdown(self, source: str, meta: TMetadata) -> str:
        source = source.strip()
        self.md_renderer.reset()
        html = self.md_renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        html = self.render_autodoc(html)

        if imports := meta.get("imports"):
            if not isinstance(imports, dict):
                raise ValueError("Invalid 'imports' in metadata, must be a dict")
            html = self._render_mdjx(html, imports)

        return html

    def render_autodoc(self, html: str):
        while True:
            match = RX_AUTODOC.search(html)
            if not match:
                break
            name = match.group(1)

            kwargs: dict[str, t.Any] = dict(arg.split("=") for arg in match.group(2).split())

            show_name = kwargs.pop("name", "1").lower() not in ("false", "0", "no")
            show_members = kwargs.pop("members", "1").lower() not in ("false", "0", "no")
            include = (kwargs.pop("include", "").split(",")) if "include" in kwargs else ()
            exclude = (kwargs.pop("exclude", "").split(",")) if "exclude" in kwargs else ()
            kwargs["ds"] = self.autodoc(
                name,
                show_name=show_name,
                show_members=show_members,
                include=include,
                exclude=exclude,
            )
            if "level" in kwargs:
                kwargs["level"] = int(kwargs["level"])

            try:
                frag = self.docs.catalog.render("autodoc.jinja", **kwargs)
            except jx.JxException as err:
                raise RuntimeError(f"Error rendering autodoc for {name}") from err
            frag = str(frag).replace("<br>", "").strip()
            start, end = match.span(0)
            html = f"{html[:start]}{frag}{html[end:]}"

        return html

    def _render_mdjx(self, source: str, imports: dict[str, str]) -> str:
        OPEN_REPL = "\u0002"
        CLOSE_REPL = "\u0003"
        source = source.replace("{", OPEN_REPL).replace("}", CLOSE_REPL)
        jx_imports = "\n".join(f'{{# import "{path}" as {name} #}}' for name, path in imports.items())
        html = self.docs.catalog.render_string(f"{jx_imports}\n{source}")
        html = str(html).replace(OPEN_REPL, "{").replace(CLOSE_REPL, "}")
        return html

    def set_prev_next(self) -> None:
        """Set the previous and next references for each page in the
        given list of pages. This modifies the pages in place.
        """
        last_index_with_next = len(self.pages) - 1

        for i, page in enumerate(self.pages):
            if i > 0:
                prev_page = self.pages[i - 1]
                page.prev = PageRef(
                    id=prev_page.id,
                    title=prev_page.title,
                    url=prev_page.url,
                    section=prev_page.section_title
                )
            else:
                page.prev = None

            if i < last_index_with_next:
                next_page = self.pages[i + 1]
                page.next = PageRef(
                    id=next_page.id,
                    title=next_page.title,
                    url=next_page.url,
                    section=next_page.section_title
                )
            else:
                page.next = None

    def set_search_data(self) -> None:
        """Set the search data for each page."""
        for page in self.pages:
            page.search_data = search.extract_search_data(page)
