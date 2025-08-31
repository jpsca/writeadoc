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
from uuid import uuid4

import jx
import markdown
from markupsafe import Markup

from . import search, utils
from .autodoc import Autodoc
from .types import PageData, PageRef, SectionRef, SiteData, TSearchData, TSiteData
from .utils import logger


TPages = dict[str, list[str]]
TProcPages = list[tuple[SectionRef, list[PageData]]]

RX_AUTODOC = re.compile(r"<p>\s*:::\s+([\w\.]+)((?:\s+\w+=\w+)*)\s*</p>")


class Docs:
    pages: TPages
    site: SiteData
    prefix: str = ""

    views_dir: Path
    pages_dir: Path
    build_dir: Path
    assets_dir: Path

    search_data: TSearchData

    def __init__(
        self,
        root: str,
        /,
        *,
        pages: TPages,
        site: TSiteData | None = None,
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

        site = site or {}
        self.site = SiteData(**site)

        self.md_renderer = markdown.Markdown(
            extensions=[
                *utils.DEFAULT_MD_EXTENSIONS,
            ],
            extension_configs={**utils.DEFAULT_MD_CONFIG},
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
        self.build(devmode=False, archive=archive)
        print("Documentation built successfully.")
        if archive:
            print(f"Archived documentation is available in the `archive/{self.site.version}` directory.")
        else:
            print("Documentation is available in the `build` directory.")

    def cli_run(self) -> None:
        """Run the documentation server and watch for changes."""
        self.build()  # Initial buil
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
        print("Building documentation...")

        self.build_dir = Path(mkdtemp(prefix="wad-")) if devmode else self.root_dir / "build"
        self.init_catalog()

        if archive:
            self.prefix = f"{self.prefix}/{self.site.version}" if self.prefix else self.site.version
            self.site.archived = True
            self.build_dir = self.archive_dir

        if self.prefix:
            self.site.base_url = f"{self.site.base_url}/{self.prefix}"

        proc_pages = self.process_pages()
        self.site.pages = proc_pages
        self.search_data = search.extract_search_data(proc_pages)

        for _, sec_pages in proc_pages:
            self.render_pages(sec_pages)

        self.render_search_page()
        self.render_index_page()
        self.render_docs_redirect_page()

        if devmode:
            self.symlink_assets()
        else:
            self.add_prefix_to_urls()
            self.copy_assets()

        for variant in self.variants.values():
            variant.build(devmode=devmode, archive=archive)

    def process_pages(self) -> TProcPages:
        proc_pages = []
        pages_list = []

        def iter_pages(files, section):
            _pages = []
            for item in files:
                if isinstance(item, dict):
                    for dir_title, dir_files in item.items():
                        if not dir_files:
                            continue
                        dir_pages = iter_pages(dir_files, section)
                        page = PageData(
                            section=section,
                            title=dir_title,
                            pages=dir_pages,
                            url=dir_pages[0].url if dir_pages else "",
                        )
                        _pages.append(page)
                else:
                    page = self.process_page(item, section)
                    pages_list.append(page)
                    _pages.append(page)
            return _pages

        for section_name, files in self.pages.items():
            section = SectionRef(
                id=uuid4().hex,
                title=section_name,
                url="",
            )
            sec_pages = iter_pages(files, section)
            if sec_pages:
                section["url"] = sec_pages[0].url
            proc_pages.append((section, sec_pages))

        # --- Add prev/next navigation links ---

        last_index_with_next = len(pages_list) - 1

        for i, page in enumerate(pages_list):
            if i > 0:
                page.prev = PageRef(
                    id=pages_list[i - 1].id,
                    title=pages_list[i - 1].title,
                    url=pages_list[i - 1].url,
                )
            else:
                page.prev = None

            if i < last_index_with_next:
                page.next = PageRef(
                    id=pages_list[i + 1].id,
                    title=pages_list[i + 1].title,
                    url=pages_list[i + 1].url,
                )
            else:
                page.next = None

        return proc_pages

    def process_page(self, filename: str, section: SectionRef) -> PageData:
        filepath = self.pages_dir / self.prefix / filename
        meta, html = self.process_file(filepath)

        url = f"/docs/{Path(filename).with_suffix('').as_posix().strip('/')}/"
        if self.prefix:
            url = f"/{self.prefix}{url}"

        mtime = filepath.stat().st_mtime
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

        return PageData(
            section=section,
            title=meta.pop("title", filepath.name),
            description=meta.pop("description", ""),
            url=url,
            meta=meta,
            content=html,
            updated_at=mtime_str,
        )

    def process_file(self, filepath: Path) -> tuple[dict[str, t.Any], str]:
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        logger.debug("Processing page: %s", filepath.relative_to(self.pages_dir / self.prefix))
        source = filepath.read_text(encoding="utf-8")
        meta, source = utils.extract_metadata(source)
        html = self.render_markdown(source)
        return meta, Markup(html)

    def render_markdown(self, source: str) -> str:
        source = source.strip()
        html = self.md_renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        html = self.render_autodoc(html)
        return html

    def markdown_filter(self, source: str, code: str = "") -> str:
        source = dedent(source.strip("\n")).strip()
        if code:
            source = f"\n```{code}\n{source}\n```\n"
        html = self.md_renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        return Markup(html)

    def render_autodoc(self, html: str):
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

    def render_pages(self, pages: list[PageData]) -> None:
        for page in pages:
            if page.pages:
                self.render_pages(page.pages)
            else:
                self.render_page(page)

    def render_page(self, page: PageData) -> None:
        outpath = self.build_dir / str(page.url).strip("/") / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        html = self.catalog.render(
            page.view,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def render_search_page(self) -> None:
        outpath = self.build_dir / self.prefix / "search" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/search/" if self.prefix else "/search/"

        page = PageData(
            section=SectionRef(id="", title="Search", url=url),
            title="Search",
            url=url,
            view="search.jinja"
        )

        html = self.catalog.render(
            page.view,
            search_data=self.search_data,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def render_docs_redirect_page(self) -> None:
        section = self.site.pages[0] if self.site.pages else None
        if not section:
            return
        # Use the first page in the section or the section itself if no pages
        url = section[1][0].url if section[1] else section[0]["url"]
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

    def render_index_page(self) -> None:
        outpath = self.build_dir / self.prefix / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/" if self.prefix else "/"

        md_index = self.pages_dir / self.prefix / "index.md"
        if md_index.exists():
            mtime = md_index.stat().st_mtime
            mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

            meta, html = self.process_file(md_index)
            page = PageData(
                id="index",
                section=SectionRef(id="", title=self.site.name, url=url),
                title=meta.get("title", self.site.name),
                url=url,
                view="index.jinja",
                description=meta.get("description", ""),
                content=html,
                updated_at=mtime_str,
            )
        else:
            # Just render the template page
            page = PageData(
                section=SectionRef(id="", title=self.site.name, url=url),
                title=self.site.name,
                url=url,
                view="index.jinja",
            )

        html = self.catalog.render(
            page.view,
            globals={"page": page}
        )
        outpath.write_text(html, encoding="utf-8")

    def symlink_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.exists():
            shutil.rmtree(target_path)

        target_path.symlink_to(self.assets_dir, target_is_directory=True)

    def copy_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        shutil.copytree(
            self.assets_dir,
            target_path,
            dirs_exist_ok=True,
        )

    def add_prefix_to_urls(self) -> None:
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
