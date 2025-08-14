import argparse
import re
import shutil
import signal
import types
import typing as t
from multiprocessing import Process
from pathlib import Path
from uuid import uuid4

import jinja2
import markdown
from markupsafe import Markup

from . import search, utils
from .types import PageData, PageRef, SectionRef, SiteData, TSiteData, TSearchData
from .utils import logger


TPages = dict[str, list[str]]
TProcPages = list[tuple[SectionRef, list[PageData]]]


class Docs:
    pages: TPages
    site: SiteData
    views: types.ModuleType
    prefix: str = ""

    pages_dir: Path
    build_dir: Path
    assets_dir: Path

    renderer: markdown.Markdown
    jinja_env: jinja2.Environment
    search_data: TSearchData

    def __init__(
        self,
        root: str,
        /,
        *,
        pages: TPages,
        views: types.ModuleType,
        site: TSiteData | None = None,
        variants: dict[str, t.Self] | None = None,
        md_extensions: list[str] = utils.DEFAULT_MD_EXTENSIONS,
        md_config: dict[str, dict[str, t.Any]] = utils.DEFAULT_MD_CONFIG,
    ):
        root_dir = Path(root).resolve().parent
        if not root_dir.exists():
            raise FileNotFoundError(f"Path {root} does not exist.")
        self.root_dir = root_dir
        self.pages_dir = root_dir / "content"
        self.assets_dir = root_dir / "assets"
        self.build_dir = root_dir / "build"
        self.archive_dir = root_dir / "archive"

        self.pages = pages
        self.views = views
        for prefix, variant in (variants or {}).items():
            variant.prefix = prefix
        self.variants = variants or {}

        site = site or {}
        self.site = SiteData(**site)

        self.strings = getattr(views.strings, self.site.lang, {})
        self.jinja_env = jinja2.Environment(
            extensions=[
                "jinja2.ext.loopcontrols",
            ],
            undefined=jinja2.StrictUndefined,
        )

        self.renderer = markdown.Markdown(
            extensions=md_extensions,
            extension_configs=md_config,
            output_format="html",
            tab_length=2,
        )

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

        if archive:
            self.prefix = f"{self.prefix}/{self.site.version}" if self.prefix else self.site.version
            self.site.archived = True
            self.build_dir = self.archive_dir

        if self.prefix:
            self.site.base_url = f"{self.site.base_url}/{self.prefix}"

        proc_pages = self.process_pages()
        self.site.pages = [
            (
                section,
                [
                    PageRef(id=page.id, title=page.title, url=page.url)
                    for page in sec_pages
                    if len(sec_pages) > 1
                ],
            )
            for section, sec_pages in proc_pages
        ]

        self.search_data = search.extract_search_data(proc_pages)

        self.render_pages(proc_pages)
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

        for section_name, files in self.pages.items():
            section = SectionRef(
                id=uuid4().hex,
                title=section_name,
                url="",
            )
            sec_pages = []

            for filename in files:
                page = self.process_page(filename, section)
                sec_pages.append(page)

            if sec_pages:
                section["url"] = sec_pages[0].url
            proc_pages.append((section, sec_pages))

        # --- Add prev/next navigation links ---

        pages_list = [page for _, sec_pages in proc_pages for page in sec_pages]
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
        filepath = self.pages_dir / filename
        meta, html = self.process_file(filepath)

        url = f"/docs/{Path(filename).with_suffix('').as_posix().strip('/')}/"
        if self.prefix:
            url = f"/{self.prefix}{url}"

        return PageData(
            section=section,
            title=meta.pop("title", filepath.name),
            description=meta.pop("description", ""),
            url=url,
            meta=meta,
            content=html,
        )

    def process_file(self, filepath: Path) -> tuple[dict[str, t.Any], str]:
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        logger.debug("Processing page: %s", filepath.relative_to(self.pages_dir))
        source = filepath.read_text(encoding="utf-8")
        meta, source = utils.extract_metadata(source)
        html = self.render_markdown(source)
        return meta, Markup(html)

    def render_markdown(self, source: str) -> str:
        html = self.renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        return html

    def render_pages(self, proc_pages: TProcPages) -> None:
        for _, sec_pages in proc_pages:
            for page in sec_pages:
                self.render_page(page)

    def render_page(self, page: PageData) -> None:
        outpath = self.build_dir / str(page.url).strip("/") / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        co = self.views.Page(self.jinja_env, page=page, site=self.site, _=self.translate)
        html = co.render()
        outpath.write_text(html, encoding="utf-8")

    def render_search_page(self) -> None:
        outpath = self.build_dir / self.prefix / "search" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/search/" if self.prefix else "/search/"

        page = PageData(
            section=SectionRef(id="", title="Search", url=url),
            title="Search",
            url=url,
        )
        co = self.views.SearchPage(self.jinja_env, page=page, site=self.site, _=self.translate)
        html = co.render(search_data=self.search_data)
        outpath.write_text(html, encoding="utf-8")

    def render_docs_redirect_page(self) -> None:
        section = self.site.pages[0]if self.site.pages else None
        if not section:
            return
        # Use the first page in the section or the section itself if no pages
        url = section[1][0]["url"] if section[1] else section[0]["url"]
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

        md_index = self.pages_dir / "index.md"
        if md_index.exists():
            meta, html = self.process_file(md_index)
            page = PageData(
                section=SectionRef(id="", title=self.site.name, url=url),
                title=meta.get("title", self.site.name),
                url=url,
                description=meta.get("description", ""),
                content=html,
            )
        else:
            # Just render the template page
            page = PageData(
                section=SectionRef(id="", title=self.site.name, url=url),
                title=self.site.name,
                url=url,
            )

        co = self.views.IndexPage(self.jinja_env, page=page, site=self.site, _=self.translate)
        html = co.render()
        outpath.write_text(html, encoding="utf-8")

    def symlink_assets(self) -> None:
        if not self.views.__file__:
            return
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        if target_path.exists():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                shutil.rmtree(target_path)
        target_path.symlink_to(self.assets_dir, target_is_directory=True)

    def copy_assets(self) -> None:
        if not self.views.__file__:
            return
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
                return f'{attr}={quote}/{self.prefix}/{url}/'

            new_content = rx_urls.sub(replace_url, content)
            html_file.write_text(new_content)

    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key using the strings dictionary.
        If the key does not exist, return the key itself.
        """
        string = self.strings.get(key, key)
        return string.format(**kwargs)