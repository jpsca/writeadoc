import argparse
import datetime
import json
import re
import shutil
import signal
import typing as t
from multiprocessing import Process
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

import jx
import markdown
from markupsafe import Markup

from . import search, utils
from .autodoc import Autodoc
from .types import (
    NavItem,
    PageData,
    SiteData,
    PageRef,
    TUserPages,
)
from .utils import logger, print_random_messages


RX_AUTODOC = re.compile(r"<p>\s*:::\s+([\w\.]+)((?:\s+\w+=\w+)*)\s*</p>")


class Docs:
    site: SiteData
    prefix: str = ""

    views_dir: Path
    pages_dir: Path
    build_dir: Path
    assets_dir: Path

    def __init__(
        self,
        root: str,
        /,
        *,
        pages: TUserPages,
        site: dict[str, t.Any] | None = None,
        variants: dict[str, t.Self] | None = None,
        md_extensions: list[t.Any] = utils.DEFAULT_MD_EXTENSIONS,
        md_config: dict[str, dict[str, t.Any]] = utils.DEFAULT_MD_CONFIG,
    ):
        root_dir = Path(root).resolve().parent
        if not root_dir.exists():
            raise FileNotFoundError(f"Path {root} does not exist.")
        self.root_dir = root_dir
        self.pages_dir = root_dir / "content"
        self.views_dir = root_dir / "views"
        self.assets_dir = root_dir / "assets"
        self.archive_dir = root_dir / "archive"
        self.build_dir = root_dir / "build"

        self.pages = pages
        for prefix, variant in (variants or {}).items():
            variant.prefix = prefix
        self.variants = variants or {}

        self.site = SiteData(**(site or {}))

        self.md_renderer = markdown.Markdown(
            extensions=[*md_extensions],
            extension_configs={**md_config},
            output_format="html",
            tab_length=2,
        )

        self.autodoc = Autodoc()

        self.catalog = jx.Catalog(
            filters={
                "markdown": self.markdown_filter
            },
            site=self.site,
            _=self.translate,
            _now=datetime.datetime.now(tz=datetime.timezone.utc),
            _insert_asset=self.insert_asset,
        )

    def init_catalog(self):
        strings_file = self.views_dir / "strings.json"
        if strings_file.exists():
            strings_data = json.loads(strings_file.read_text())
            self.strings = strings_data.get(self.site.lang, {})
        else:
            self.strings = {}

        self.catalog.add_folder(self.views_dir)

    def cli(self):
        parser = argparse.ArgumentParser(description="WriteADoc CLI")
        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser("run", help="Run and watch for changes")

        build_parser = subparsers.add_parser("build", help="Build the documentation for deployment")
        build_parser.add_argument(
            "--archive",
            action="store_true",
            default=False,
            help="Build the current version as an archived documentation"
        )

        args = parser.parse_args()

        if args.command == "build":
            self.cli_build(archive=args.archive)
        elif args.command in (None, "run"):
            self.cli_run()
        else:
            parser.print_help()

    def cli_build(self, archive: bool) -> None:
        """Build the documentation for deployment."""
        self.build_dir = self.root_dir / "build"
        self.build(devmode=False, archive=archive)
        print("Documentation built successfully.")
        if archive:
            print(f"Archived documentation is available in the `archive/{self.site.version}` directory.")
        else:
            print("Documentation is available in the `build` directory.")

    def cli_run(self) -> None:
        """Run the documentation server and watch for changes."""
        self.build_dir = Path(mkdtemp(prefix="wad-"))
        self.build()  # Initial build
        p = Process(
            target=utils.start_server,
            args=(str(self.build_dir),),
            daemon=True
        )
        p.start()
        utils.start_observer(self.root_dir, self.build)

        def shutdown(*args):
            p.terminate()
            p.join()
            exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

    def build(self, devmode: bool = True, archive: bool = False) -> None:
        print_random_messages()
        self.init_catalog()

        nav, pages = self._process_pages(self.pages)
        self.site.nav = nav
        self.site.pages = pages


        if archive:
            self.prefix = f"{self.prefix}/{self.site.version}" if self.prefix else self.site.version
            self.site.archived = True
            self.build_dir = self.archive_dir

        if self.prefix:
            self.site.base_url = f"{self.site.base_url}/{self.prefix}"

        for page in pages:
            self._render_page(page)
        self._render_search_page()
        self._render_index_page()
        self._render_docs_redirect_page()
        self._render_extra()

        if devmode:
            self._symlink_assets()
        else:
            self._add_prefix_to_urls()
            self._copy_assets()

        for variant in self.variants.values():
            variant.build(devmode=devmode, archive=archive)

    def markdown_filter(self, source: str, code: str = "") -> str:
        source = dedent(source.strip("\n")).strip()
        if code:
            source = f"\n```{code}\n{source}\n```\n"
        html = self.md_renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        return Markup(html)

    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key using the strings dictionary.
        If the key does not exist, return the key itself.
        """
        string = self.strings.get(key, key)
        return string.format(**kwargs)

    def insert_asset(self, asset: str) -> str:
        """
        Read the asset and return the content
        """
        asset_path = self.assets_dir / asset
        if asset_path.exists():
            return Markup(asset_path.read_text(encoding="utf-8").strip())
        return ""

    # Private

    def _process_pages(self, user_pages: TUserPages) -> tuple[list[NavItem], list[PageData]]:
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
                        "pages": [
                            "start/advanced/configuration.md",
                            "start/advanced/themes.md",
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
                    "icon": "",
                    "pages": [
                        {
                            "id": "start-advanced-configuration",
                            "title": "Configuration",
                            "url": "/docs/start/advanced/configuration/",
                            "icon": "icons/cog.svg",
                            "pages": []
                        },
                        {
                            "id": "start-advanced-themes",
                            "title": "Themes",
                            "url": "/docs/start/advanced/themes/",
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
            <Page /docs/start/advanced/configuration/>,
            <Page /docs/start/advanced/themes/>,
        ]
        ```
        """
        pages: list[PageData] = []

        def _process(user_pages: TUserPages, section: str = "") -> list[NavItem]:
            items = []

            for user_page in user_pages:
                # Section
                if isinstance(user_page, dict):
                    us_title = user_page.get("title")
                    if not us_title:
                        raise ValueError(f"Section entry is missing 'title': {user_page}")
                    us_pages = user_page.get("pages", [])
                    if not isinstance(us_pages, list) or not us_pages:
                        raise ValueError(f"Section entry has invalid or empty 'pages': {user_page}")
                    item = NavItem(
                        title=us_title,
                        url="",
                        icon=user_page.get("icon") or "",
                        pages=_process(us_pages, section=us_title),
                    )
                    items.append(item)

                # Page
                elif isinstance(user_page, str):
                    page = self._process_page(user_page, section=section)
                    pages.append(page)
                    item = NavItem(
                        title=page.title,
                        url=page.url,
                        icon=page.icon,
                    )
                    items.append(item)

                else:
                    raise ValueError(f"Invalid page entry: {user_page}")

            return items

        nav = _process(user_pages)
        self._set_prev_next(pages)
        for page in pages:
            page.search_data = search.extract_search_data(page)
        return nav, pages

    def _process_page(self, filename: str, section: str = "") -> PageData:
        filepath = self.pages_dir / self.prefix / filename
        meta, html = self._process_file(filepath)

        url = f"/docs/{Path(filename).with_suffix('').as_posix().strip('/')}/"
        if self.prefix:
            url = f"/{self.prefix}{url}"

        return PageData(
            section=section,
            title=meta.get("title", filepath.name),
            icon=meta.get("icon", ""),
            url=url,
            meta=meta,
            content=html,
        )

    def _process_file(self, filepath: Path) -> tuple[dict[str, t.Any], str]:
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        logger.debug("Processing page: %s", filepath.relative_to(self.pages_dir / self.prefix))
        source = filepath.read_text(encoding="utf-8")
        meta, source = utils.extract_metadata(source)
        html = self._render_markdown(source)
        return meta, Markup(html)

    def _render_markdown(self, source: str) -> str:
        source = source.strip()
        html = self.md_renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        html = self._render_autodoc(html)
        return html

    def _render_autodoc(self, html: str):
        while True:
            match = RX_AUTODOC.search(html)
            if not match:
                break
            name = match.group(1)

            kwargs: dict[str, t.Any] = dict(arg.split("=") for arg in match.group(2).split())

            include = (kwargs.pop("include", "").split(",")) if "include" in kwargs else ()
            exclude = (kwargs.pop("exclude", "").split(",")) if "exclude" in kwargs else ()
            kwargs["ds"] = self.autodoc(name, include=include, exclude=exclude)
            if "level" in kwargs:
                kwargs["level"] = int(kwargs["level"])

            frag = self.catalog.render("autodoc.jinja", **kwargs)
            frag = str(frag).replace("<br>", "").strip()
            start, end = match.span(0)
            html = f"{html[:start]}{frag}{html[end:]}"

        return html

    def _set_prev_next(self, pages: list[PageData]) -> None:
        """Set the previous and next references for each page in the
        given list of pages. This modifies the pages in place.
        """
        last_index_with_next = len(pages) - 1

        for i, page in enumerate(pages):
            if i > 0:
                prev_page = pages[i - 1]
                page.prev = PageRef(
                    id=prev_page.id,
                    title=prev_page.title,
                    url=prev_page.url,
                    section=prev_page.section
                )
            else:
                page.prev = None

            if i < last_index_with_next:
                next_page = pages[i + 1]
                page.next = PageRef(
                    id=next_page.id,
                    title=next_page.title,
                    url=next_page.url,
                    section=next_page.section
                )
            else:
                page.next = None

    def _render_page(self, page: PageData) -> None:
        outpath = self.build_dir / str(page.url).strip("/") / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        html = self.catalog.render(
            page.view,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def _render_search_page(self) -> None:
        outpath = self.build_dir / self.prefix / "search" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/search/" if self.prefix else "/search/"

        page = PageData(
            title="Search",
            url=url,
            view="search.jinja"
        )
        search_data = {}
        for page in self.site.pages:
            search_data.update(page.search_data or {})

        html = self.catalog.render(
            page.view,
            search_data=search_data,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def _render_index_page(self) -> None:
        outpath = self.build_dir / self.prefix / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/" if self.prefix else "/"

        md_index = self.pages_dir / self.prefix / "index.md"
        if md_index.exists():
            meta, html = self._process_file(md_index)
            page = PageData(
                id="index",
                title=meta.get("title", self.site.name),
                url=url,
                view="index.jinja",
                content=html,
            )
        else:
            # Just render the template page
            page = PageData(
                title=self.site.name,
                url=url,
                view="index.jinja",
            )

        html = self.catalog.render(
            page.view,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def _render_docs_redirect_page(self) -> None:
        first_page = self.site.pages[0] if self.site.pages else None
        if not first_page:
            return
        # Use the first page
        url = first_page.url
        if self.prefix:
            url = url.removeprefix(f"/{self.prefix}/docs/")
        else:
            url = url.removeprefix("/docs/")
        url = f"{url}index.html"

        outpath = self.build_dir / self.prefix / "docs" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url=./{url}">'
            "<title></title></head><body></body></html>"
        )
        outpath.write_text(html, encoding="utf-8")

    def _render_extra(self) -> None:
        for file in (
            "sitemap.xml",
            "robots.txt",
            "humans.txt"
        ):
            outpath = self.build_dir / self.prefix / file
            outpath.parent.mkdir(parents=True, exist_ok=True)
            try:
                body = self.catalog.render(f"{file}.jinja")
            except jx.ImportError:
                logger.info("No view found for %s, skipping...", file)
                continue
            outpath.write_text(body, encoding="utf-8")

    def _symlink_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.exists():
            shutil.rmtree(target_path)

        target_path.symlink_to(self.assets_dir, target_is_directory=True)

    def _copy_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        shutil.copytree(
            self.assets_dir,
            target_path,
            dirs_exist_ok=True,
        )

    def _add_prefix_to_urls(self) -> None:
        """Update URLs in the site data for archived documentation."""
        if not self.prefix:
            return
        rx_urls = re.compile(r"""(href|src|action|poster|data|srcset|data-src)=("|')/(docs|assets|search)/""")
        build_dir = self.build_dir / self.prefix
        for html_file in build_dir.rglob("*.html"):
            content = html_file.read_text()

            def replace_url(match: re.Match) -> str:
                attr = match.group(1)
                quote = match.group(2)
                url = match.group(3)
                return f"{attr}={quote}/{self.prefix}/{url}/"

            new_content = rx_urls.sub(replace_url, content)
            html_file.write_text(new_content)
