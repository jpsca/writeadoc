import re
import typing as t
from collections.abc import MutableMapping, Sequence
from pathlib import Path
from uuid import uuid4

from markupsafe import Markup

from . import search, utils
from .autodoc import render_autodoc
from .md import render_markdown
from .types import (
    NavItem,
    PageData,
    PageRef,
    TMetadata,
)
from .utils import logger


if t.TYPE_CHECKING:
    from .main import Docs


_RX_FILL_TAG = re.compile(
    r"{%-?\s*(?:fill\s+[0-9A-Za-z_.:$-]+|endfill)\s*-?%}"
)


class PagesProcessor:
    docs: "Docs"
    nav_items: list[NavItem]
    pages: list[PageData]

    def __init__(self, docs: "Docs"):
        """Pages processor"""
        self.docs = docs
        self.pages = []

    def run(self, user_pages: Sequence[str | dict[str, t.Any]]) -> tuple[list[NavItem], list[PageData]]:
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

        if not (self.docs.views_dir / "index.jx").exists():
            logger.warning("No index.jx view found.")
            return None

        outpath = self.docs.build_dir / self.docs.prefix / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.docs.prefix}/" if self.docs.prefix else "/"

        md_index = self.docs.content_dir / "index.md"
        if md_index.exists():
            source, meta = self.read_file(md_index)
            html, state = self.render_markdown(source, meta, filepath=md_index)
            meta.setdefault("id", "index")
            meta.setdefault("title", self.docs.site.name)
            meta.setdefault("view", "index.jx")

            return PageData(
                url=url,
                meta=meta,
                source=source,
                content=Markup(html),
                filepath=md_index,
                toc=state.get("toc_items", []),
            )

        # Just render the template page
        return PageData(
            url=url,
            meta={
                "id": "index",
                "title": self.docs.site.name,
                "view": "index.jx",
            },
        )

    def process_items(
        self,
        user_pages: Sequence[str | dict[str, t.Any]],
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
        user_page: dict[str, t.Any],
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
        parents = parents + (id,)

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
        return NavItem(title=title, id=id, url=url, icon=icon, pages=pages, closed=closed)

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

        def _render(**globals: t.Any) -> str:
            return self.docs.catalog.render("autodoc.md.jx", **globals)

        source = render_autodoc(source.strip(), render=_render)
        try:
            html, state = self.render_markdown(source, meta, filepath=filepath)
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
            toc=state.get("toc_items", []),
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

    def render_markdown(self, source: str, meta: TMetadata, filepath: Path) -> tuple[str, MutableMapping]:
        source = source.strip()
        html, state = render_markdown(source, meta=meta, __file__=str(filepath))

        if imports := meta.get("imports"):
            if not isinstance(imports, dict):
                raise ValueError("Invalid 'imports' in metadata, must be a dict")
            html = self.render_mdjx(html, imports)

        return html, state

    def render_mdjx(self, source: str, imports: dict[str, str]) -> str:
        OPEN_REPL = "\u0002"
        CLOSE_REPL = "\u0003"
        source, fill_tags = self._protect_mdjx_fill_tags(source, imports)
        source = source.replace("{", OPEN_REPL).replace("}", CLOSE_REPL)
        for token, tag in fill_tags:
            source = source.replace(token, tag)
        jx_imports = "\n".join(
            f'{{# import "{path}" as {name} #}}' for name, path in imports.items()
        )
        html = self.docs.catalog.render_string(f"{jx_imports}\n{source}")
        html = str(html).replace(OPEN_REPL, "{").replace(CLOSE_REPL, "}")
        return html

    def _protect_mdjx_fill_tags(
        self,
        source: str,
        imports: dict[str, str],
    ) -> tuple[str, list[tuple[str, str]]]:
        if "{%" not in source:
            return source, []

        names = [re.escape(name) for name in imports]
        if not names:
            return source, []

        tag_rx = re.compile(rf"<(?P<tag>{'|'.join(names)})(?=\s|/|>)")
        fill_tags: list[tuple[str, str]] = []

        def protect_fill(match: re.Match[str]) -> str:
            token = f"\u0004WAD_FILL_{len(fill_tags)}\u0005"
            fill_tags.append((token, match.group(0)))
            return token

        result = []
        pos = 0

        while match := tag_rx.search(source, pos):
            tag = match.group("tag")
            tag_end = self._find_tag_end(source, match.end())
            if tag_end == -1:
                pos = match.end()
                continue

            if source[match.start():tag_end].rstrip().endswith("/>"):
                pos = tag_end
                continue

            close_start, close_end = self._find_closing_tag(source, tag, tag_end)
            if close_start == -1:
                pos = tag_end
                continue

            result.append(source[pos:tag_end])
            result.append(_RX_FILL_TAG.sub(protect_fill, source[tag_end:close_start]))
            result.append(source[close_start:close_end])
            pos = close_end

        if not result:
            return source, fill_tags

        result.append(source[pos:])
        return "".join(result), fill_tags

    def _find_closing_tag(self, source: str, tag: str, pos: int) -> tuple[int, int]:
        open_rx = re.compile(rf"<{re.escape(tag)}(?=\s|/|>)")
        close_tag = f"</{tag}>"
        close_len = len(close_tag)
        depth = 1

        while depth:
            next_open = open_rx.search(source, pos)
            next_close = source.find(close_tag, pos)

            if next_close == -1:
                return -1, -1

            if next_open and next_open.start() < next_close:
                tag_end = self._find_tag_end(source, next_open.end())
                if tag_end == -1:
                    return -1, -1
                if not source[next_open.start():tag_end].rstrip().endswith("/>"):
                    depth += 1
                pos = tag_end
                continue

            depth -= 1
            if depth == 0:
                return next_close, next_close + close_len
            pos = next_close + close_len

        return -1, -1

    def _find_tag_end(self, source: str, pos: int) -> int:
        in_single_quotes = False
        in_double_quotes = False

        for i in range(pos, len(source)):
            ch = source[i]
            if ch == "'" and not in_double_quotes:
                in_single_quotes = not in_single_quotes
            elif ch == '"' and not in_single_quotes:
                in_double_quotes = not in_double_quotes
            elif ch == ">" and not in_single_quotes and not in_double_quotes:
                return i + 1

        return -1

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
                    section=prev_page.section_title,
                )
            else:
                page.prev = None

            if i < last_index_with_next:
                next_page = self.pages[i + 1]
                page.next = PageRef(
                    id=next_page.id,
                    title=next_page.title,
                    url=next_page.url,
                    section=next_page.section_title,
                )
            else:
                page.next = None

    def set_search_data(self) -> None:
        """Set the search data for each page."""
        for page in self.pages:
            page.search_data = search.extract_search_data(page)
